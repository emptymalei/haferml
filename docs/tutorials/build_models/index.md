# Build Models

HaferML provides three main classes for model building,

- [`haferml.model.dataset.DataSet`][haferml.model.dataset.DataSet], which holds the data and necessary functions such as creating train test splits,
- [`haferml.model.modelset.ModelSet`][haferml.model.modelset.ModelSet], which holds the model definition and supporting functions such as hyperparameter related functions,
- [`haferml.model.workflow.ModelWorkflow`][haferml.model.workflow.ModelWorkflow], which is used to combine the DataSet and ModelSet.

The reason that we split the DataSet and ModelSet is that we will mostly need ModelSet in predictions. Thus when using the model, we will only load the ModelSet.
