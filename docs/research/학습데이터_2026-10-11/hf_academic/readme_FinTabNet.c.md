---
license: cdla-permissive-2.0
tags:
- table structure recognition
- table extraction
---

# FinTabNet.c

The FinTabNet.c dataset was released in 2023.

You can think of FinTabNet.c as a fork (a modified version, in this case by different authors) of the original FinTabNet dataset.

FinTabNet.c contains:
- automated corrections of FinTabNet (such as canonicalization) to correct oversegmentation and to make the dataset more consistent with other TSR datasets, like PubTables-1M
- fewer samples than FinTabNet, where samples were removed whose annotations could not be either automatically processed, corrected, or verified

For more details about this version (2023) of the dataset and the adjustments made to the original dataset, please see ["Aligning benchmark datasets for table structure recognition"](https://arxiv.org/abs/2303.00716).

For the code used to create this dataset, see [https://github.com/microsoft/table-transformer](https://github.com/microsoft/table-transformer).

## Citing

If you use this dataset in your published work, please cite:
```
@article{smock2023aligning,
  title={Aligning benchmark datasets for table structure recognition},
  author={Smock, Brandon and Pesala, Rohith and Abraham, Robin},
  booktitle={International Conference on Document Analysis and Recognition},
  pages={371--386},
  year={2023},
  organization={Springer}
}
```

## About the original FinTabNet dataset

Please see: [https://developer.ibm.com/data/fintabnet/](https://developer.ibm.com/data/fintabnet/) (link last checked September 2023).

### Original license

According to the dataset website, the license of the original FinTabNet dataset is [CDLA-Permissive](https://cdla.dev/permissive-1-0/).