import elastix_napari
import itk
from elastix_napari import elastix_registration

# empyt test
print(elastix_napari.napari_experimental_provide_dock_widget())

# add your tests here...
# elastix_registration.elastix_registration(None, None, None, Nonse, 'rigid', ('par.txt', 'par.txt'))

#
# fixed_image = itk.imread('data/CT_2D_head_fixed.mha', itk.F)
# moving_image = itk.imread('data/CT_2D_head_moving.mha', itk.F)
# fixed_mask = itk.imread('data/CT_2D_head_fixed_mask.mha', itk.F)
# moving_mask = itk.imread('data/CT_2D_head_moving_mask.mha', itk.F)

# image, label = elastix_registration.elastix_registration(
#                 fixed_image, moving_image, fixed_mask, moving_mask, 'rigid',
#                 'data/parameters_Rigid.txt', True)
image = elastix_registration.elastix_registration()
# assert label('name') == 'rigid Registration'
