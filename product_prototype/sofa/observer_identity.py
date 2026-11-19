"""Frozen compiled-observer identities; never label live edited C++ as an old build."""
from native_bending_coupon import BASE,sha

IDENTITIES={
    '463':('build_mode_observer463','native_beam_mode_fd464','13e497228eb290fcae75a701113dd2be5d8af7f894e7179aa633d1734a31e483','e1ca5da4442eabed8b0cef2c3bf96b681fa0d593665aaa3c875e13a3449c12f5'),
    '458':('build_loaded_observer458','native_beam_loaded_fd459','6b941c36b76713ea107d10dd7d3dbceea651784f3695d456dd1543c64282479a','7637bd0b7928f7fc95e93fd60b0be586935da3765c3b575c2e882f33addcf61b'),
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

def compiled_strain_observer():
    binary=BASE/'cad/build_strain_observer469/libReGripNativeStrainObserver.so'
    source=BASE/'results/native_beam_strain470/Observer.cpp'
    if sha(binary)!='4f5aede3ad22bca3144ad442885a09ab1236684631c7a44dc57fec8691a6589c' or sha(source)!='4bb9800d9b776799e7bdfa42c3d3247d10ae69ca1e2b24bad934ca6e6521aec6':
        raise ValueError('frozen strain observer identity mismatch')
    return binary,source

def compiled_alarm_window():
    binary=BASE/'cad/build_alarm_window484/libReGripAlarmWindow.so'
    source=BASE/'results/b3_alarm_window485/AlarmController.cpp'
    if sha(binary)!='6da7c82044b72a024bc825a476020e75f99499ad4f51c106b0a00b36bde841bf' or sha(source)!='0fc9234e959d76f94218e6c4dd123d4b65940665e725baf3ec051dacf8e8f8bf':
        raise ValueError('frozen native alarm controller identity mismatch')
    return binary,source

def compiled_pair_rows():
    binary=BASE/'cad/build_pair_rows512/libReGripPairRows.so'
    source=BASE/'results/b3_direct_rows513/Observer.cpp'
    if sha(binary)!='6a00b4e75ef314f5d92ebc67431ee36cedba02c91e6546ff28a4ffe9d5514527' or sha(source)!='2334142b2609a4132f1a96696475d0e527e4246dab22fe92905d9d3cbd25eb99':
        raise ValueError('frozen direct-J observer source/binary mismatch')
    return binary,source

def compiled_feature_rows():
    binary=BASE/'cad/build_feature_rows554/libReGripFeatureRows.so'
    source=BASE/'results/b3_finite_features555/Observer.cpp'
    if sha(binary)!='f2a8ca3a35608b5b62719cbbf6a09dea5f38fa6670fa7b73d603d06ffe597b59' or sha(source)!='eb0149022d83fe5b6636a080dfcadaf40204722fdbdb24da8b0990ad6139869b':
        raise ValueError('frozen Native feature observer source/binary mismatch')
    return binary,source
