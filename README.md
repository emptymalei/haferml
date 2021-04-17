# Hafer ML

The HomemAde FramEwoRk for Machine Learning (HAFER ML) is a minimal and unambitious framework for your machine learning projects, with reproducibility in mind.

> Hafer is oat in German.

## Install

```
pip install haferml
```

This will leave out many dependencies. To install all,

```
pip install "haferml[all]"
```

The extras options:
- `all`: everything
- `aws`: required if one needs AWS
- `docs`: required to build the docs


## The Idea

The Hafer ML frameworks is very simple. It is a minimal framework that I have been applying to small projects. Hafer ML save the artifacts at every step to make it easy to reproduce. The tool we choose to make it reproducible is Docker.

![](https://datumorphism.leima.is/blog/data-science/assets/a-simple-machine-learning-framework/simple_framework_ml_projects.png)
> [on whimsical](https://whimsical.com/hafer-ml-WMGCWpDixJG9S3PAFWey1i)

