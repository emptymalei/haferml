# Documentation for HAFER ML

The HomemAde FramEwoRk for Machine Learning (HAFER ML).

> Hafer is oat in German.

![](assets/linkedin_banner_image_2.png)

## Install

```
pip install haferml
```

This will leave out many dependencies. To install haferml together with all the requirements,

```
pip install "haferml[all]"
```

The extras options:

- `all`: everything
- `aws`: required if one needs AWS
- `docs`: required to build the docs

## The Idea

The Hafer ML framework is designed to be a minimal framework for data scientists. Hafer ML uses config files and saves the artifacts at every step for reproducibility.

![](https://datumorphism.leima.is/blog/data-science/assets/a-simple-machine-learning-framework/simple_framework_ml_projects.png)

## Toolkit

The essential tools are

- Python,
- Docker,
- AWS: such as S3, ECR and ECS.

