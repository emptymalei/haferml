# Data Manipulation

There are several philosophies in transforming the dataset. For example, some methods will transform the data in a column based style while some other methods will perform the transformation in a row based style. HaferML implemented utilities for both of these styles.

## Transformer

[`haferml.etl.transform.pipeline.Transformer`][haferml.etl.transform.pipeline.Transformer] is a row-based transformer that transforms one row into the data we need. There are several advantages of this type of transformation,

- we can simply drop the record if it can not be used, and
- we can easily stream the data as it comes in.

## Ordered Transformer

HaferML does not have a dedicated transformer for column-based transformations. The reason is that we can easily do this using [`haferml.preprocess.ingredients.OrderedProcessor`][haferml.preprocess.ingredients.OrderedProcessor] or build our own using [`haferml.preprocess.ingredients.with_transforms`][haferml.preprocess.ingredients.with_transforms] and [`haferml.preprocess.ingredients.order`][haferml.preprocess.ingredients.order] or [`haferml.preprocess.ingredients.attributes`][haferml.preprocess.ingredients.attributes] with each step being some column based operations.

With pandas, column based transformations are much easier than the previous row-based method.


