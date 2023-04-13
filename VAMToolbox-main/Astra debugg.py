import astra
import numpy as np
vg = astra.create_vol_geom(2, 32, 32)
pg = astra.create_proj_geom('parallel3d', 1, 1, 32, 32, [0])
vol = np.random.rand(32, 2, 32)
(sino_id, sino) = astra.create_sino3d_gpu(vol, pg, vg)
astra.data3d.delete(sino_id)
err = np.max(np.abs(sino[:,0,:] - np.sum(vol,axis=1)))