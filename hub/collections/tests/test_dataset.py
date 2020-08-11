import numpy as np
import pytest
from hub.collections import dataset, tensor


def test_tensor_getitem0():
    t = tensor.from_array(np.array([1, 2, 3, 4, 5], dtype="int32"))
    assert t[2].compute() == 3


def test_tensor_getitem1():
    t = tensor.from_array(np.array([1, 2, 3, 4, 5], dtype="int32"))
    assert t[2:4].shape == (2,)
    assert (t[2:4].compute() == np.array([3, 4], dtype="int32")).all()


def test_tensor_getitem2():
    t = tensor.from_array(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype="int32"))
    assert t[1:3, 1:3].shape == (2, 2)
    assert (t[1:3, 1:3].compute() == np.array([[5, 6], [8, 9]], dtype="int32")).all()


def test_tensor_iter():
    t = tensor.from_array(np.array([1, 2, 3, 4, 5], dtype="int32"))
    n = list(t)
    assert [x.compute() for x in n] == [1, 2, 3, 4, 5]


def test_tensor_meta():
    t = tensor.from_array(
        np.array([[1, 2, 3, 4], [4, 5, 6, 7], [7, 8, 9, 10]], dtype="int32")
    )
    assert t.ndim == 2
    assert len(t) == 3
    assert t.shape == (3, 4)
    assert t.dtype == "int32"


def test_tensor_dtag():
    t = tensor.from_array(np.array([1, 2], dtype="int32"), dtag="image")
    ds = dataset.from_tensors({"name": t})
    ds.store("./data/new/test")
    ds = dataset.load("./data/new/test")
    assert ds["name"].dtag == "image"


def test_dataset_len():
    t1 = tensor.from_array(
        np.array([[1, 2, 3, 4], [4, 5, 6, 7], [7, 8, 9, 10]], dtype="int32")
    )
    t2 = tensor.from_array(np.array([1, 2, 3], dtype="int32"))
    t3 = tensor.from_array(
        np.array([[1, 2, 3, 4, 6], [4, 5, 6, 7, 6], [7, 8, 9, 10, 6]], dtype="int32")
    )
    ds = dataset.from_tensors({"t1": t1, "t2": t2, "t3": t3})
    assert len(ds) == 3


def test_dataset_iter():
    t1 = tensor.from_array(np.array([[1, 2], [4, 5], [7, 8]], dtype="int32"))
    t2 = tensor.from_array(np.array([1, 2, 3], dtype="int32"))
    ds = dataset.from_tensors({"t1": t1, "t2": t2})
    items = list(ds)
    assert len(items) == 3
    for item in items:
        assert isinstance(item, dict)
    for item in items:
        assert sorted(item.keys()) == ["t1", "t2"]
    assert (items[0]["t1"].compute() == np.array([1, 2], dtype="int32")).all()
    assert (items[1]["t1"].compute() == np.array([4, 5], dtype="int32")).all()
    assert (items[2]["t1"].compute() == np.array([7, 8], dtype="int32")).all()
    assert items[0]["t2"].compute() == 1
    assert items[1]["t2"].compute() == 2
    assert items[2]["t2"].compute() == 3


def test_dataset_getitem_str():
    t1 = tensor.from_array(np.array([[1, 2], [4, 5], [7, 8]], dtype="int32"))
    t2 = tensor.from_array(np.array([1, 2, 3], dtype="int32"))
    ds = dataset.from_tensors({"t1": t1, "t2": t2})
    ds = ds["t1", "t2"]
    assert ds["t1"] is t1
    assert ds["t2"] is t2


def test_dataset_getitem_index():
    t1 = tensor.from_array(np.array([[1, 2], [4, 5], [7, 8]], dtype="int32"))
    t2 = tensor.from_array(np.array([1, 2, 3], dtype="int32"))
    ds = dataset.from_tensors({"t1": t1, "t2": t2})
    assert (ds[0:2]["t1"].compute() == np.array([[1, 2], [4, 5]], dtype="int32")).all()
    assert (ds[0:2]["t2"].compute() == np.array([1, 2], dtype="int32")).all()


def test_dataset_getitem_str_index():
    t1 = tensor.from_array(np.array([[1, 2], [4, 5], [7, 8]], dtype="int32"))
    t2 = tensor.from_array(np.array([1, 2, 3], dtype="int32"))
    ds = dataset.from_tensors({"t1": t1, "t2": t2, "t3": t2})
    ds = ds[["t1", "t2"], 0:2]
    assert (ds["t1"].compute() == np.array([[1, 2], [4, 5]], dtype="int32")).all()
    assert (ds["t2"].compute() == np.array([1, 2], dtype="int32")).all()


def test_dataset_store_load():
    t1 = tensor.from_array(np.array([[1, 2], [4, 5], [7, 8]], dtype="int32"))
    t2 = tensor.from_array(np.array([1, 2, 3], dtype="int32"))
    ds = dataset.from_tensors({"t1": t1, "t2": t2})
    path = "./data/test_store_tmp/store_load"
    ds = ds.store(path)
    assert (
        ds["t1"].compute() == np.array([[1, 2], [4, 5], [7, 8]], dtype="int32")
    ).all()
    assert (ds["t2"].compute() == np.array([1, 2, 3], dtype="int32")).all()


def test_dataset_store_load_big():
    t1 = tensor.from_array(np.zeros(shape=(2 ** 10, 2 ** 13), dtype="int32"))
    ds = dataset.from_tensors({"t1": t1})
    path = "./data/test_store_tmp/store_load_big"
    ds = ds.store(path)
    assert (
        ds["t1"].compute() == np.zeros(shape=(2 ** 10, 2 ** 13), dtype="int32")
    ).all()


def test_dataset_merge():
    t1 = tensor.from_array(
        np.array([[1, 2, 3, 4], [4, 5, 6, 7], [7, 8, 9, 10]], dtype="int32")
    )
    t2 = tensor.from_array(np.array([1, 2, 3], dtype="int32"))
    t3 = tensor.from_array(
        np.array([[1, 2, 3, 4, 6], [4, 5, 6, 7, 6], [7, 8, 9, 10, 6]], dtype="int32")
    )

    ds1 = dataset.from_tensors({"t1": t1, "t2": t2})
    ds2 = dataset.from_tensors({"t3": t3})
    ds = dataset.merge([ds1, ds2])
    assert sorted(ds.keys()) == ["t1", "t2", "t3"]


def test_dataset_concat():
    t1 = tensor.from_array(np.array([5, 6, 7], dtype="int32"))
    t2 = tensor.from_array(np.array([1, 2, 3], dtype="int32"))
    ds1 = dataset.from_tensors({"t1": t1})
    ds2 = dataset.from_tensors({"t1": t2})
    ds = dataset.concat([ds1, ds2])
    assert len(ds) == 6
    assert (ds["t1"].compute() == np.array([5, 6, 7, 1, 2, 3], dtype="int32")).all()


def test_store_empty_dataset():
    t = tensor.from_array(np.array([], dtype="uint8"))
    ds = dataset.from_tensors({"empty_tensor": t})
    try:
        ds = ds.store("./data/hub/empty_dataset")
    except Exception as e:
        pytest.fail(f"failed storing empty dataset {str(e)}")


class UnknownCountGenerator:
    def meta(self):
        return {
            "arr": {"shape": (-1, 5), "dtype": "int32"},
            "rra": {"shape": (-1,), "dtype": "int32"},
        }

    def __call__(self, input):
        arr = np.zeros(shape=(input, 5), dtype="int32")
        rra = np.zeros(shape=(input,), dtype="int32")
        for x in range(input):
            for i in range(5):
                arr[x, i] = x + i
            rra[x] = x
        return {"arr": arr, "rra": rra}


def test_unknown_size_input():
    ds = dataset.generate(UnknownCountGenerator(), range(1, 11))
    assert ds["arr"].shape == (-1, 5)
    assert ds["rra"].shape == (-1,)
    ds = ds.store("./data/test_store_tmp/unknown_count")
    assert len(ds) == 55
    assert (
        ds["rra"][:10].compute()
        == np.array([0, 0, 1, 0, 1, 2, 0, 1, 2, 3], dtype="int32")
    ).all()
    assert ds["rra"][9].compute() == 3
    assert (ds["arr"][5].compute() == np.array([2, 3, 4, 5, 6], dtype="int32")).all()


def test_s3_dataset():
    ds = dataset.generate(UnknownCountGenerator(), range(1, 3))
    assert ds["arr"].shape == (-1, 5)
    assert ds["rra"].shape == (-1,)
    ds = ds.store("s3://snark-test/test_dataflow/test_s3_dataset")
    # dzevakan comment
    assert len(ds) == 3
    assert (ds["rra"][:3].compute() == np.array([0, 0, 1], dtype="int32")).all()
    assert ds["rra"][2].compute() == 1
    assert (ds["arr"][1].compute() == np.array([0, 1, 2, 3, 4], dtype="int32")).all()


def test_to_pytorch():

    try:
        import torch
    except ImportError:
        print("Pytorch hasn't been imported and tested")
        return

    t1 = tensor.from_array(np.array([[1, 2], [3, 4]], dtype="int32"))
    np_arr = np.empty(2, object)
    np_arr[0] = np.array([5, 6, 7, 8], dtype="int32")
    np_arr[1] = np.array([7, 8, 9], dtype="int32")
    # np_arr[:] = [np_arr0, np_arr1]
    t2 = tensor.from_array(np_arr)
    ds = dataset.from_tensors({"t1": t1, "t2": t2})
    torch_ds = ds.to_pytorch()
    train_loader = torch.utils.data.DataLoader(
        torch_ds, batch_size=1, num_workers=0, collate_fn=torch_ds.collate_fn
    )
    data = list(train_loader)
    assert len(data) == 2
    for i in range(2):
        assert "t1" in data[i]
        assert "t2" in data[i]
    assert data[0]["t1"][0].tolist() == [1, 2]
    assert data[0]["t2"][0] == [5, 6, 7, 8]
    assert data[1]["t1"][0].tolist() == [3, 4]
    assert data[1]["t2"][0] == [7, 8, 9]


def test_to_backend_with_tf_and_pytorch():
    try:
        import torch
        import tensorflow
    except ImportError:
        print("Pytorch hasn't been imported and tested")
        return

    ds = dataset.load("mnist/mnist")

    tfds = ds.to_tensorflow()
    ptds = ds.to_pytorch()
    ptds = torch.utils.data.DataLoader(
        ptds,
        batch_size=1,
        num_workers=1,
        collate_fn=ds.collate_fn if "collate_fn" in dir(ds) else None,
    )

    for i, (batchtf, batchpt) in enumerate(zip(tfds, ptds)):
        gt = ds["labels"][i].compute()
        assert gt == batchtf["labels"].numpy()
        assert gt == batchpt["labels"].numpy()
        if i > 10:
            break


def test_to_backend_with_tf_and_pytorch():
    try:
        import torch
        import tensorflow
    except ImportError:
        print("Pytorch hasn't been imported and tested")
        return

    ds = dataset.load("mnist/mnist")

    tfds = ds.to_tensorflow().batch(8)
    ptds = ds.to_pytorch()
    ptds = torch.utils.data.DataLoader(
        ptds,
        batch_size=8,
        num_workers=8,
        collate_fn=ds.collate_fn if "collate_fn" in dir(ds) else None,
    )
    for i, (batchtf, batchpt) in enumerate(zip(tfds, ptds)):
        assert np.all(batchtf["labels"].numpy() == batchpt["labels"].numpy())
        if i > 10:
            break