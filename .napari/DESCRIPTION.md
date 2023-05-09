# Description

This plugin makes the elastix toolbox for rigid and nonrigid registration of images available in napari.
elastix is open source software, based on the well-known Insight Segmentation and Registration Toolkit (ITK). The software consists of a collection of algorithms that are commonly used to solve (medical) image registration problems. The modular design of elastix allows the user to quickly configure, test, and compare different registration methods for a specific application.

# Who is This For?

With this plugin both 2D and 3D images in all file formats available in ITK can be registered.
The plugin supports various transformations including rigid, affine and bspline.

Registration within the plugin is done based on user defined parameters, but for novice users
defaults for each transformation model are available.

# How to Guide

Load the images you want to register into napari and select them in the fixed (or reference) and moving image dropdowns of plugin interface.

For fast and easy registration only the preferred transformation (rigid, affine or bspline) has to be selected (see Transformations section for explanation).

For more advanced registrations the following adjustments can be made in the plugin:

- Masks for both the fixed and the moving images can be selected to let elastix only include certain areas in the registration. These masks have to be loaded into napari and selected in the correct mask dropdown menus, which appear when the masks box is ticked.
- Point sets for both the fixed and the moving images can de selected to use certain points to aid registration. These point set files have to be .txt files in the following format:

  index/point\
  #points\
  point1 x point1 y [point1 z]\
  point2 x point2 y [point2 z]

  The first line indicates whether the points are given as “indices” (of the fixed image), or as “points” (in
  physical coordinates). The second line stores the number of points that will be specified. After that the
  point data is given. For example:

  point\
  3\
  2.32 5.34 -4.12\
  -1.56 0.12 9.23\
  1.00 7.34 -0.23

- An initial transform file that specifies a transform that is applied before the registration is done, can be uploaded as a .txt file. For the latest file and transform formats that are supported, see the [elastix manual](https://elastix.lumc.nl/doxygen/index.html)

- For the most common registration parameters adjustments can be made in the plugin GUI

- Other, less common registration parameters can be adjusted by uploading custom transform parameter file(s). (Select 'custom' in the preset dropdown).


<img width="1438" alt="Screenshot 2021-05-12 at 15 07 24" src="https://user-images.githubusercontent.com/33719474/117980045-d6009b00-b333-11eb-9976-f64d34f4f7cc.png">

# Transformations

In the plugin 3 common transformations are available as presets, other transformations can be done with the 'custom' option in the preset dropdown. The plugin then has the ability to upload custom parameter files in which other transformations can be specified.

The three common transformations are:

- [Rigid Transform](https://en.wikipedia.org/wiki/Rigid_transformation):
Also known as a Euclidean transformation, this transform preserves the Euclidean
distance between each pair of points on the image. This includes rotation,
translation and reflection but not scaling or shearing.


- [Affine Transform](https://en.wikipedia.org/wiki/Affine_transformation):
This transfrom preserves
lines and parallelism, but not necessarily distance and angles. Translation,
scaling, similarity, reflection, rotation and shearing are all valid
affine transformations.

- [BSpline Transform](https://en.wikipedia.org/wiki/B-spline):
This is a deformable transformation that preserves none of the properties mentioned in the transforms describe above.

# Getting Help
If you find a bug in the elastix napari plugin, or would like support with using it, please raise an
issue on the [GitHub repository](https://github.com/SuperElastix/elastix-napari).

For question specifically about the elastix toolbox we have a [mailing list](https://groups.google.com/forum/#!forum/elastix-imageregistration).

# Contributions
Contributions to the elastix-napari plugin, [itkelastix](https://github.com/InsightSoftwareConsortium/ITKElastix) (the python wrapper) or [elastix](https://github.com/SuperElastix/elastix) (the C++ core) on which the plugin is build, are welcome.
