"""Frozen compiled-observer identities; never label live edited C++ as an old build."""
from native_bending_coupon import BASE,sha

IDENTITIES={
    '456':('build_unit_observer456','native_beam_units457','831fd04b007973d2554f661ba6ff65c406713591409fbb55c64f5c61768b9a3f','16fa6e24f192a46779eea712fa1381eb1adbbb3143b200cdf6e1e7f9ba782bd1'),
    '451':('build_accepted_observer451','native_beam_accepted452','f26d44cf6721c514b72dbd1dcfb28a257399e0f2697743a1330d628ed6b35acd','9674de6b5c85051c52b1b055e09e8725393e71319d6e639fbcb6a42cb1aaa9ef'),
    '441':('build_private_rigid441','native_beam_private_force442','afe612f0372849d6077134b64d7519332a91058196b514f066dcdf558a29a9bb','ceadd757a6d134be84f5f59aa29219f57955af1ebf704ec4ed04ec52e3797d42'),
    '438':('build_reference_precision438','native_beam_reference_precision439','e87bf12bd20536775f1c2a050aecc80a02a7e40cd150d9873726eafb25967c1f','7ec6421cc915a636cd57155c5c8fed67df415e9c159c916cf0e0702c483faf3c'),
    '431':('build_reference_observer431','native_beam_reference432','97340d138aec5733550ef60a4bec8296e355a75deaf64c6cc547622f8ef0dcf8','11fb14726ed0c020a33eb504905cfb577b4f99325113bcf2dfaab89238e89d14'),
    '400':('build_elastic_observer400','native_matrix_assess402','effbb80334e70ecb805b1643fef8e488b671008dff96104e1a17d770c44309e2','c2e3eac945fdbe6ccb4bb66817077db453f900d2d1092327238af03b5a1fb7f7'),
    '406':('build_elastic_probe406','native_loaded_sections407','792b0b37c794e2db4c347bb52856410434be0712c42f38ad144121dde9f924ed','e143096e607ab25c0740254b8bd66a7983a3bd6b1ba6a1ec447925b52e514f53'),
    '410':('build_assembled_observer410','native_bending_matrix_paths415','0fb661dd48f9a28f266a987b11482227ea19e62205eb06f8f43284d3cc393f83','51b004b5b0022db006d92762f2f10175060eefe32db9ce8f0907130a6d5c29b3'),
    '428':('build_rigid_observer428','native_rigid_tangent429','ebb517b8c1a9f016cdbea06f07c4914cbc341f34eb4f16acd46e0cdf7f5460a3','0cf7421083eec9f01d8c175b1dfaab4dd4396f06a7467e9fa0e5e50a3be916f0'),
}

def compiled_observer(identifier):
    build,case,source_hash,binary_hash=IDENTITIES[identifier]
    binary=BASE/'cad'/build/'libReGripElasticObserver.so'
    source=BASE/'results'/case/'Observer.cpp'
    if sha(binary)!=binary_hash or sha(source)!=source_hash:
        raise ValueError('frozen compiled observer source/binary mismatch;do not substitute live source')
    return binary,source
