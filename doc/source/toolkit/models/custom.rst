Custom
======

This page lists the classes available for ACT-derived models that fit the toolkit scope:

.. currentmodule:: ansys.aedt.toolkits.antenna.backend.antenna_models.custom

.. autosummary::
   :toctree: _autosummary

   GPSPatchCeramic

Assessment notes
----------------

``GPS_patch_ceramic`` was added because its ACT implementation is explicit parametric geometry
that can be standardized in the toolkit.

``UHF_Probe`` was not added because the ACT plugin only inserts a bundled ``.a3dcomp`` asset.
It does not expose synthesis equations or editable source geometry, which would make the toolkit
depend on an opaque ACT-only binary component instead of a standardizable model.
