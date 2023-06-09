import cupy as cp
import cupyx.scipy.ndimage
# cp.cuda.set_allocator(None)
# cp.cuda.set_pinned_memory_allocator(None)
import numpy as np
import scipy.ndimage
import pyfftw
# try:
#     import cupy.fft as fft_method
# except:
#     import mkl_fft as fft_method

from mkl_fft import _numpy_fft
import mkl_fft
import matplotlib.pyplot as plt
import  matplotlib.colors
import display_functions as disp
from time import perf_counter
"""
GPU accelerated fft2
https://www.idtools.com.au/gpu-accelerated-fft-compatible-numpy/
"""



"""
EXAMPLE OF PARAMETER DEFINITIONS

# optical params only have an effect if used with P_type = 'gauss'
optical_params = {
    'NA':                   0.1,    # numerical aperture
    'n':                    1.48,   # refractive index of monomer
    'focal_offset':         30e-6,      # focal plane offset from axis of rotation (m)
    'alpha':                0,      # absorption coefficient (1/m); NOTE still deciding how absorption should be incorporated for Gauss beam (in Gauss kernel or in backprojector)
    'w0':                   3e-6,  # beam waist radius (m)
    'voxel_size':           1e-6   # physical dimension of voxel (m); NOTE none of the other projectors have physical units yet, still working on it
}
"""



class gauss2D():
    def __init__(self,target,proj_params,optical_params):
        """
        Parameters
        ----------
        target : ndarray
            target array or array with equivalent size
        proj_params : dict
            parameters defining projector configuration
        optical_params : dict
            optical parameters for defining the Gaussian beam
        """
        self.NA = optical_params['NA']
        self.n = optical_params['n']
        self.offset = optical_params['focal_offset']
        self.alpha = optical_params['alpha']
        self.w_pixel = np.sqrt(2/np.pi)*optical_params['DMD_pixel_size']
        self.w_psf = 1.62*optical_params['wavelength']*optical_params['n']/(np.pi*optical_params['NA']*np.sqrt(2*np.log(2)))
        self.w0 = np.sqrt(self.w_psf**2 + (self.w_pixel**2) * (optical_params['magnification']**2))
        self.voxel_size = optical_params['voxel_size']
        self.target = target
        self.angles = proj_params['angles']
        self.angles_rad = np.deg2rad(self.angles)

        self.nProp, self.nT = self.target.shape
        self.coords = self.setupInterpCoords(2)
        # self.nT = int(np.ceil(np.sqrt(2) * max(self.target.shape[0],self.target.shape[1])))


        self.kernel, self.FFT_kernel = self.createGaussKernel()
        
            
        
    def createGaussKernel(self):
        """
        Builds Gaussian kernel and Fourier-transformed kernel according 
        to the optical parameters specified in optical_params

        Returns
        -------
        kernel : ndarray
            single pixel Gaussian beam approximation with same size as 
            target
        FFT_kernel : ndarray
            kernel Fourier-transformed along dimensions orthogonal to 
            propagation
        """
        

        t = np.linspace(-self.nT*self.voxel_size/2,
                        self.nT*self.voxel_size/2,
                        self.nT)
        prop = np.linspace(-self.nProp*self.voxel_size/2,
                            self.nProp*self.voxel_size/2,
                            self.nProp)


        Prop, T = np.meshgrid(prop,t,indexing='ij')

        Prop = Prop - self.offset
        R = T
        zr = self.n*self.w0/self.NA
        print('ZR: %f' % zr)
        # TODO need to decide how to incorporate absorption
        # should it be in the kernel? Then we have to assume spatial invariance which
        # is incorrect for cylindrical vial
        # should it be element-wise multiplication in the backprojector? 
        wz = self.w0*np.sqrt(1+(Prop/zr)**2)
        I0 = 2/(np.pi*self.w0**2)
        kernel = I0 * (self.w0/wz)**2 * np.exp(-2*R**2/wz**2) * np.exp(-Prop*self.alpha)

        # focal_plane_i = int(self.offset/self.voxel_size + self.nProp/2)
        # if focal_plane_i >= kernel.shape[0]:
        #     focal_plane_i = kernel.shape[0] - 1
        #     print('Warning: Focal offset is larger than half the reconstruction space.\nOffset was set to the maximum.')
        
        # Normalize kernel with sum of row with maximum sum (usually at the focus unless absorption is specified)
        max_ind = np.argmax(kernel.sum(axis=1))
        kernel = kernel/np.sum(kernel[max_ind,:])

        # kernel = kernel/np.sum(kernel[int(self.offset/self.voxel_size + self.nProp/2),:])
        # kernel = kernel/kernel.sum(axis=1)[:,None]
        # kernel = kernel/(np.sqrt(2*np.pi)*kernel.std(axis=1)[:,None])

        # disp.view_plot(kernel,'kernel')


        fig, ax = plt.subplots(1,1)
        im = ax.imshow(np.where(kernel>1e-20,kernel,1e-20),cmap='CMRmap',extent=[t.min()*1e6,t.max()*1e6,prop.min()*1e6,prop.max()*1e6],norm=matplotlib.colors.LogNorm())
        # im = ax.imshow(kernel,cmap='inferno',extent=[t.min()*1e6,t.max()*1e6,prop.min()*1e6,prop.max()*1e6])
        cbar = fig.colorbar(im, ax=ax)
        cbar.ax.set_title('Intensity [a.u.]')
        ax.set_xlabel('t [µm]')
        ax.set_ylabel('s [µm]')
        plt.show()

        FFT_kernel = np.fft.fft(kernel,axis=1)            



        return kernel, FFT_kernel

    def setupInterpCoords(self,dimension,angle=None):
    
        x = np.linspace(-self.nT/2,self.nT/2,self.nT)
        y = np.linspace(-self.nProp/2,self.nProp/2,self.nProp)
        YY, XX = np.meshgrid(y, x, indexing='ij')
        limits = [(-self.nProp/2, self.nProp/2), (-self.nT/2, self.nT/2)]

        coords_all_angles = []

        for curr_angle in np.nditer(self.angles_rad):
            t = YY*np.sin(curr_angle) - XX*np.cos(curr_angle)
            prop = YY*np.cos(curr_angle) + XX*np.sin(curr_angle)

            # interpolate onto reconstruction grid and sum
            ti = np.ravel(t)
            propi = np.ravel(prop)

            coords = [(c - lo) * (n - 1) / (hi - lo) for (lo, hi), c, n in zip(limits, [propi,ti], self.target.shape)]
            coords_all_angles.append(coords)

        coords_ret = coords_all_angles


        return cp.asarray(coords_ret)

    def convolveWithGaussKernelFP(self,target):

        FFT_target = mkl_fft.fft(target,axis=1)
        
        convolved_target = np.real(np.fft.ifftshift(mkl_fft.ifft(np.multiply(FFT_target,self.FFT_kernel)),axes=1))

        return cp.asarray(convolved_target)

    def convolveWithGaussKernelBP(self,projection):
        """
        Convolves a 1D or 2D projection with a 1D or 2D Gauss kernel defined at each 
        propagation distance to generate the backprojection for the angle
        of the projection.
            1D
            f*_theta(x,y) = fft(P_theta(t)) * fft(G(t,prop))

            2D
            f*_theta(x,y,z) = fft(P_theta(t,z)) * fft(G(t,prop,z))

        Parameters
        ----------
        projection : ndarray
            1D projection in t (lateral) or 2D projection in t (lateral)
            and z (height) axes at a single projection angle

        Returns
        -------
        convolved_backproj : ndarray
            convolved backprojection in spatial domain for the same angle
            of the input projection
        """

        # Fourier transform projection
        FFT_projection = mkl_fft.fft(projection)


        convolved_backproj = np.real(np.fft.ifftshift(mkl_fft.ifft(np.multiply(FFT_projection[np.newaxis,:],self.FFT_kernel)), axes=1))

        return convolved_backproj
    


    def gaussFP(self,target):

        targetcp = cp.asarray(target)
        projections = cp.zeros((self.nT,len(self.angles_rad)))
        
        for curr_angle_ind in range(len(self.angles_rad)):

            # interpolated = scipy.ndimage.map_coordinates(curr_backproj,coords,order=1,mode='constant',cval=0)
            # reconstruction += np.reshape(interpolated,reconstruction.shape)
            interpolated = cupyx.scipy.ndimage.map_coordinates(targetcp,self.coords[curr_angle_ind],order=1,mode='constant',cval=0)
            rotated = cp.reshape(interpolated,target.shape)

            rotated = self.convolveWithGaussKernelFP(cp.asnumpy(rotated))


            projections[:, curr_angle_ind] = cp.sum(rotated,axis=0)
        
        projections = cp.asnumpy(projections)

 

        return projections

    def gaussBP(self,projections):

        reconstruction = cp.zeros(self.target.shape)

        for curr_angle_ind in range(len(self.angles_rad)):
            # convolve 2D projection with each slice (in propagation axis) 
            # of precomputed Gaussian kernel
            curr_backproj = self.convolveWithGaussKernelBP(projections[:,curr_angle_ind])

            # interpolated = scipy.ndimage.map_coordinates(curr_backproj,coords,order=1,mode='constant',cval=0)
            # reconstruction += np.reshape(interpolated,reconstruction.shape)
            interpolated = cupyx.scipy.ndimage.map_coordinates(cp.asarray(curr_backproj),self.coords[curr_angle_ind],order=1,mode='constant',cval=0)
            reconstruction += cp.reshape(interpolated,reconstruction.shape)

        reconstruction = cp.asnumpy(reconstruction)     


        return reconstruction * np.pi / (2* len(self.angles))
    
    def forwardProject(self,target):
        if np.any(target<0):
            neg_target = -np.clip(target,a_min=None,a_max=0)
            pos_target = np.clip(target,a_min=0,a_max=None)               
            neg_projections = self.gaussFP(neg_target)
            pos_projections = self.gaussFP(pos_target)
            
            projections = pos_projections + (-neg_projections)

        else:
            projections = self.gaussFP(target)

        return projections

    def backProject(self,projections):
        reconstruction = self.gaussBP(projections)

        return reconstruction
if __name__ == "__main__":


    font = {'family' : 'sans-serif',
            'sans-serif'  : 'arial',
            'weight' : 'bold',
            'size'   : 36}

    matplotlib.rc('font', **font)

    voxel_size = float(2e-6)
    # testing generation of kernels
    target = np.zeros((256,256))
    a = 30
    target[128-a:128+a,128-a:128+a] = 1
    # target = np.zeros((256,256))
    # a = 30
    # target[128-a:128+a,128-a:128+a] = 1
 
    num_angles = 36  # number of projection angles in 180°
    angles = np.linspace(0, 360 - 360 / num_angles, num_angles)

    proj_params = {
        'angles': angles
    }
    optical_params = {
        'wavelength': 405e-9,
        'NA':  0.2,
        'n':    1.48,
        'DMD_pixel_size': 10.6e-6,
        'magnification': 45.0/125.0,
        'focal_offset': 0e-6,
        'alpha': 0,
        'voxel_size': voxel_size
    }



    G = gauss2D(target,proj_params,optical_params)

    proj = G.gaussFP(target)
    disp.view_plot(proj,'Proj')
    # fig, ax = plt.subplots(1,1)
    # im = ax.imshow(proj,cmap='inferno',extent=[0,359,-target.shape[0]*2/2,target.shape[0]*2/2])
    # cbar = fig.colorbar(im, ax=ax)
    # ax.set_xlabel('Angle [°]')
    # ax.set_ylabel('t [µm]')
    # plt.show()

    bp = G.gaussBP(proj)
    disp.view_plot(bp,'Proj')
    # fig, ax = plt.subplots(1,1)
    # im = ax.imshow(bp,cmap='inferno',extent=[-target.shape[0]*optical_params['voxel_size']/2,target.shape[0]*optical_params['voxel_size']/2,-target.shape[0]*optical_params['voxel_size']/2,target.shape[0]*optical_params['voxel_size']/2])
    # cbar = fig.colorbar(im, ax=ax)
    # cbar.ax.set_title('Intensity [a.u.]')
    # ax.set_xlabel('x [µm]')
    # ax.set_ylabel('y [µm]')
    # plt.show()

    plot_extents = np.array([-target.shape[0],target.shape[0],-target.shape[0],target.shape[0]])*voxel_size/2*1e6

    fig, ax = plt.subplots(1,1)
    im = ax.imshow(bp/np.amax(bp),extent=plot_extents,cmap='inferno')
    ax.set_ylabel('y [µm]')
    ax.set_xlabel('x [µm]')
    cbar = plt.colorbar(im, ax=ax)
    cbar.ax.set_title('Norm Dose')
    plt.show()
    # proj = np.zeros_like(G.kernel[:,0])
    # proj[128] = 1
    # # proj[380:-1] = 0
    # # disp.view_plot(proj,'proj')
    # bp = G.convolveWithGaussKernelBP(proj)
    # fig, ax = plt.subplots(1,1)
    # bp = np.where(bp>0,bp,0)
    # bp_ = np.ma.array(bp, mask= bp<=0).min(0)
    # bp_new = np.where(bp == 0, bp_, bp)
    
    # cmap = plt.cm.get_cmap("viridis")
    # cmap.set_bad(cmap.colors[0])
    # plt.imshow(bp_new, norm=matplotlib.colors.LogNorm(vmin=np.nanmin(bp_new), vmax=np.nanmax(bp_new)), cmap=cmap)
    # plt.colorbar()
    # ax.set_ylabel('y [µm]')
    # ax.set_xlabel('x [µm]')
    # plt.show()

 