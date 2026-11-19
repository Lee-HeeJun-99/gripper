"""Frozen compiled-observer identities; never label live edited C++ as an old build."""
from native_bending_coupon import BASE,sha

IDENTITIES={
    '400':('build_elastic_observer400','native_matrix_assess402','effbb80334e70ecb805b1643fef8e488b671008dff96104e1a17d770c44309e2','c2e3eac945fdbe6ccb4bb66817077db453f900d2d1092327238af03b5a1fb7f7'),
    '406':('build_elastic_probe406','native_loaded_sections407','792b0b37c794e2db4c347bb52856410434be0712c42f38ad144121dde9f924ed','e143096e607ab25c0740254b8bd66a7983a3bd6b1ba6a1ec447925b52e514f53'),
    '410':('build_assembled_observer410','native_bending_matrix_paths415','0fb661dd48f9a28f266a987b11482227ea19e62205eb06f8f43284d3cc393f83','51b004b5b0022db006d92762f2f10175060eefe32db9ce8f0907130a6d5c29b3'),
}

def compiled_observer(identifier):
    build,case,source_hash,binary_hash=IDENTITIES[identifier]
    binary=BASE/'cad'/build/'libReGripElasticObserver.so'
    source=BASE/'results'/case/'Observer.cpp'
    if sha(binary)!=binary_hash or sha(source)!=source_hash:
        raise ValueError('frozen compiled observer source/binary mismatch;do not substitute live source')
    return binary,source
