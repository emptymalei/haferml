# HAFER ML Changelog

## 2021-05-20, 0.0.12

We have added two new decorators for convenience.

`order`

In the previous version, we had `attributes`. Most of the time, we do not care about which attribute name that we used if we just need to order the member functions.

For this reason, we created this new decorator `order` and simply use `@order(1)` and we are done.

`with_transforms`

If one would like to write a customized transform class, it takes a lot of effort in the previous version of the package. Now we can simply apply the decorator `@with_transforms` and the member function can access the ordered transforms using `self.transforms`.


## 2021-05-09, 0.0.11

1. Added config generation tool.

## 2021-05-09, 0.0.10

1. Change `BasePreProcessor` member function name and make it more flexible.