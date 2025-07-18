from lenstronomy.LensModel.Solver.solver2point import Solver2Point
from lenstronomy.LensModel.Solver.solver4point import Solver4Point
import numpy as np

__all__ = ["Solver"]


class Solver(object):
    """Joint solve class to manage with type of solver to be executed and checks whether
    the requirements are fulfilled."""

    def __init__(self, solver_type, lensModel, num_images, parameter_module=None):
        """

        :param solver_type: string, option for specific solver type
         see detailed instruction of the Solver4Point and Solver2Point classes
        :param lensModel: instance of a LensModel() class
        :param num_images: int, number of images to be solved for
        :param parameter_module: a class to be used with solver_type that has routines to be used in the Solver4Point
         module for parameter handling: extract_array, update_kwargs, and add_fixed_lens
        """
        self._num_images = num_images
        self._lensModel = lensModel
        if self._num_images == 4:
            self._solver = Solver4Point(
                lensModel, solver_type=solver_type, parameter_module=parameter_module
            )
        elif self._num_images == 2:
            self._solver = Solver2Point(lensModel, solver_type=solver_type)
        else:
            raise ValueError(
                "%s number of images is not valid. Use 2 or 4!" % self._num_images
            )

    def constraint_lensmodel(self, x_pos, y_pos, kwargs_list, xtol=1.49012e-12):
        """

        :param x_pos: x-position constraints on images
        :param y_pos: y-position constraints on images
        :param kwargs_list: lens model keyword argument list
        :param xtol: tolerance level of solution when to stop the non-linear solver
        :return: updated lens model that satisfies the lens equation for the point sources, accuracy
        """
        return self._solver.constraint_lensmodel(x_pos, y_pos, kwargs_list, xtol=xtol)

    def update_solver(self, kwargs_lens, x_pos, y_pos):
        """


        :param kwargs_lens: lens model keyword argument list
        :param x_pos: x-position constraints on images
        :param y_pos: y-position constraints on images
        :return: updated lens model that satisfies the lens equation for the point sources
        """

        if not len(x_pos) == self._num_images:
            raise ValueError(
                "Point source number %s must be as specified by the solver with number of images %s"
                % (len(x_pos), self._num_images)
            )
        kwargs_lens, precision = self.constraint_lensmodel(x_pos, y_pos, kwargs_lens)
        return kwargs_lens

    def check_solver(self, image_x, image_y, kwargs_lens):
        """Returns the precision of the solver to match the image position.

        :param kwargs_lens: full lens model (including solved parameters)
        :param image_x: point source in image
        :param image_y: point source in image
        :return: precision of Euclidean distances between the different rays arriving at
            the image positions
        """
        source_x, source_y = self._lensModel.ray_shooting(image_x, image_y, kwargs_lens)
        dist = np.sqrt((source_x - source_x[0]) ** 2 + (source_y - source_y[0]) ** 2)
        return dist

    def add_fixed_lens(self, kwargs_fixed_lens, kwargs_lens_init):
        """Returns kwargs that are kept fixed during run, depending on options.

        :param kwargs_fixed_lens: keyword argument list of fixed parameters (indicated
            by fitting argument of the user)
        :param kwargs_lens_init: Initial values of the full lens model keyword arguments
        :return: updated kwargs_fixed_lens, added fixed parameters being added (and
            replaced later on) by the non-linear solver.
        """
        kwargs_fixed_lens = self._solver.add_fixed_lens(
            kwargs_fixed_lens, kwargs_lens_init
        )
        return kwargs_fixed_lens
