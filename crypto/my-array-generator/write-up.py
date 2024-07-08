#!/usr/bin/env python3
import random
import os

"""
To make things more readable, 
1. I will insert comments the line before on things that I have changed with ###.
2. I will name my variables my_var_XXXXX.
"""

### Use a key that has no repeat characters
KEY = b"DUCTF{AB12E3GHIJKLMNOPQRS45VWXY}"
KEY_SIZE = 32
F = 2**14


class MyArrayGenerator:
    def __init__(self, key: bytes, n_registers: int = 128):
        self.key = key
        self.n_registers = n_registers

    def prepare(self):
        self.registers = [0 for _ in range(self.n_registers)]
        self.key_extension(self.key)

        self.carry = self.registers.pop()
        self.key_initialisation(F)

    def key_extension(self, key: bytes):
        if len(key) != KEY_SIZE:
            raise ValueError(f"Key length should be {KEY_SIZE} bytes.")

        for i in range(len(self.registers)):
            j = (4 * i) % KEY_SIZE
            subkey = key[j : j + 4]
            self.registers[i] = int.from_bytes(subkey)

    def key_initialisation(self, F: int):
        for _ in range(F):
            self.update()

    def shift(self):
        self.registers = self.registers[1:]

    def update(self):
        r0, r1, r2, r3 = self.registers[:4]

        self.carry ^= r1 if r2 > r3 else (r1 ^ 0xFFFFFFFF)

        self.shift()
        self.registers.append(self.registers[-1] ^ self.carry)

    def get_keystream(self) -> int:
        byte_index = random.randint(0, 3)
        byte_mask = 0xFF << (8 * byte_index)
        return (self.registers[-1] & byte_mask) >> (8 * byte_index)

    def encrypt(self, plaintext: bytes):
        self.prepare()

        """
        Given that the update is a series of XOR, the key would cancel out each other after repeating cycle,
        Let's capture the order of these changes.
        """
        ct = b""
        ### my_var_count is just a counter for the character position in plaintext.
        my_var_count = 0
        ### my_var_map to store the map order of keystream used to the index of KEY.
        my_var_map = []
        for b in plaintext:
            self.update()
            my_var_ks = self.get_keystream()

            ### As character above 0x80 would be non-ascii, we can assume that the registers XOR by 0xFFFFFFFF in the process
            my_var_char = bytes([my_var_ks^0xff]) if my_var_ks & 0x80 else bytes([my_var_ks])
            if my_var_char in KEY:
                my_var_map.append((my_var_count, KEY.index(my_var_char)))
            ct += int.to_bytes(my_var_ks ^ b)
            my_var_count += 1

        return ct, my_var_map

    def decrypt(self, ciphertext: bytes) -> bytes:
        return self.encrypt(ciphertext)


if __name__ == "__main__":
    random.seed(1234)
    cipher = MyArrayGenerator(KEY)

    plaintext = os.urandom(1280)
    print(f'plaintext = "{plaintext.hex()}"')

    ### See the encrypt method
    ciphertext, my_var_map = cipher.encrypt(plaintext)
    print(f'ciphertext = "{ciphertext.hex()}"')

    ### Now that we have the my_var_map, let's sub in the given plaintext and ciphertext
    my_var_plaintext = "144f3fe104f33fb1db5cd69e1cc18ceb6abbb2424bbd7ed83835d6c4af215ab9865379bf361f8c145689fa7cfa1c8a0c0254f0ef9fefb9559c45e2550d90de096e6b390280009763416f43b1c52005009f499d5c221f7b7b32f9f1f766b8057d5daf1d46a9e6547b2b655df872312a155a24f3ce66a08455006d54dcb3fea2b692010892d63503009904505d729e4b06784347d9d8f097352b73e98129122f59e62886527326022a529b58fcfe2a038b54053cc57123032aba5356e20641fba1ae9bd5398916e29cd2ec2ad01dad60ab2f4b3cbdc17afdfd5f777ac341c0a94581fc1f87782103ab61137f24b605266b8d20a2b295fee2819ce56b4436b7e106e613c6f3a6fcb2f9417b34bbec90874701b4a9402afb242ceab4c7f873a95537334b8ccab122a6dd46fcd818a11b65f3e37863ec1c27c5f832ab3e8c42a26db4d5d6362deb9af2d736390722d28c0e809f0f58b6f3cb079b64f22eeb4a4fe56307b5f4829f218afd7a13e9d1a7f3bcc4dfee5d83d4600c6c1cf69530a3413568a31251e533c9be324e7bb7b977dce081f82793001457f17383a58d8eb8f7dfc72c67f7ca0ac952257e5bf5881255564867ab8e8198c314309e211dd3d29b88d206c6111ca98aa9bf1f7c8ae2ebbd6fa1f73229b349c76bccc1c0e3460bcb350c06efac3d1503273da0f388e35fc7e4d8e22bcbe5204d7e3c05019689957b80d28bdcf4ff3536a640c0aca822e0943e559c7e5bc475aebc4459f55e95e0972e76d2ca23a7e5dd5e9762bc360dbfed8c2459cc54d5f1825dec6a0ef09de00bc6b9e87d8b8bfeca3722de36116cb549d7b45d4b7ee72af3c9d78e8358e33b2aa0ce3f91380da77cfc32d9e3f635703519da183aefe078dda73fc450b8cc899a4f90cee20597a5be5eec67e98f69f9801b6063d77c270c821ae71e1fb16a1fe66c68fc39d3c1ff75e1d78a2a42cc0bd737b90d6c22ada2e1ef041094adb7c341cb228d2b5f353bef801a9ac657274196ef91212c310eb41b6e7aa6c03178d3c8796731bfe41e54ee2092d5ae85679e77d2872761bf6001aefe68c83ea4b1968af3ab81de5fbe163eddb86a84efcdcb7cd77a335b1ebd75a6b2b913c6f579b4e80c21321cdc53bc5753d3d6f446d5cecc962c6f308ae80441026378a0556b49a40d62a500839197ae7b44a8595dee3b9ec358a495c73009d82f948b560a41fcad13530f81fe94604e1f95fd9fc47b0e94f1693f28aa470eb07f1f1ce73c40a818c517a9af0eb8b655e8de065b791291d1be9c3d4ead2aca027e4303f04650a6a812d156711dd29d54a8b84362e3d186c1ffee12c72e9a907c41b1963ab30d02dffbaf04e2c8d5fc383f8d469ae708fd91730db423a2a6d4eb6503b74923c04d754f190ab7bee78a53540a82e7b98260d84ac0159ff2759a0cbce70885a9ee46e0ed88091d1ed93146e916be84b28bb0a5e808684769d68fd7f392952d1a6d3b5a858eef6411abe859cb6a78a16d8f269a8d17d8bf81782695b3f41f15e90d03b0103c7e2ee3010db34b699f1354d9a3ecf3a1f7da0e510af3301f76dad2f180d75368f6fee0c673c3d20a6b02efd33c742a2cdaafa1365e797652816a2a443fff8efff3ff761b235b5959ee0cbbc22f56fbb1f8869e048760a3d5fcc17fd12433b9e3721e2197d703ae7d3a4c01a9e370541a9963190d63d4390697c65d1f5f4bb33b4237c1a08ef6503f4d6fae907b71fbd528668ca3eeb6dfd3a6421675cfc973e398f671f35f0194e3ac69bfbef73dd29af81fe3249ba829af79bb3ea26808512f"
    my_var_ciphertext = "3810d227b7ca7cb8cc9afa35679e154b763623db53428127a858c5c75e199088883d9b94bb4b4cbd3276e3c2e9d132832067362974d6e4a3898376003da1aba9ece6ff649800979c58d450216dc4cfce6e427f7736b444afd5f9ac548ad40f0d510ff07f43051772678671adf691e47b46c04c577e5f7baae92c070e9d660dbcd291b055dc47026e845bdcbe5e357bc8a9bc205223ee16a440d3883d1976a569341917791426022a3dc7f4d1ea77c47e1637842194c72344f187dad900146a6fd110254d79160faca1dfb4856636153abe7aad92a685fdfd49e5f91124a7d0b1d331eef772ef0dc4b34c0caf4950e90dee3e17c6f21f82def29752edf0f39d596b8be79598a069954b6018e4fe90347c7342be34d5afb6143987d5c139f47118ab4b8c354e22bf99c06fc4812b8a16ac782d0d8869b6478a12c5eca731bee0423d12bbd218aacadd1bed74e446c8c1b1fcee577b6bf9eaab0ae9e842b4ddb63c7517d02b599af3918fe741434a35f00052e7b64740dc4a33bd3b78a1cdcc8abc441247b99fe2dbfdd8eaa92adfc715b3e52d8e2b0003c9783e6878d1c783950ad71307076a699ee9eba4bf2a84a1e217146f1ac51c5867a24c533d426f9820ea0c2251339034d02fee4422d1067b842aaa0b3cc7dd831002bef262d4e8faa42762104a836928cc969862372e55b7eeeac22029ba3d89c2ca26aab75dc47b802d6d4e8d936b962ad1f3f3c9769b0f4df5804f9d5d7410ef1b2acc1d6a0baea376c5be0f0d29296b5a7a9308ae0aee82d0756cdc13bbd67c3cab525cc26d93469646821b2882954576b7c3bc5ef2ad65c65c41764727c875113bde86b55fd5a0ce9d03419d39dc895f12719289e16a6aeacab7cf70d52144a41562f2018d84a2cf0242e861a926f1194ab6fc52f93ba20400a302b621b014125e1cbf7105284c62b71249a624a179d728b811e7258a0fb3ec03c163c195fd697ea5ed63db4134dde26a15a5a589f5ba51f5db8cd0a76500a3a111610988cfdaf8de3e7823d66e0afa2df62788b359989e0e88a36733bce1adf3730d6b581453273cb38abade61939bc5316ad76268759ff43c5f5ebac24358f08fdbbbc826e66e6dc5e0c77adeef8db54453435745709c9bd875a85da5e0a939c69c2805cdf8f8a05ae0d1456d5269a045a86a05fd2be3f92ef217cb0c3e95f8f390cfd8c5779ba0468768164c23c59a193dee0af396ba58e816e369bb3d56b8b428048832d23c1288e025bafa380750e803260a65b97f359811643563c3d04e717765f79ce3f11340eb6931c3e3ce71852d1c9b9c2acba4107329cb407ee7232256567c0d3a2a03a4cb9675c8b40e907705c5552c8e4cea4f57759171c2cd4de2c96c9b8071aa26976028d76b365b48a85c1a7ebf5eeb7714126ae93fae26ac69ce1eacc928669e6f88171f1288668f0d146f2265787224cfdfddaef239286c68bbc54702763d72239b77b9d84807a01717b7d6791838381c2c753a008f4eb52ceb289eb979e184c426e8d76fe8d0d1f55d74ecd1593019f94956757f91c3b76f057153ba720bc1caa7d1285397e0bac4aa12635864186f67d376bb8527910f2df0a12c0d0d50952e763b74f06ec033e3ddde9430531953def2f400604ea5eb1d5be2cbf3dfaec238ca2efe5b73c6cabbf017d73582d3f712c67debd8d5f2509bb6dab20897150b4549c44bb33ba4768bcf9290360f7ecf3ba988d3ab20ca4d0028e81d4e1d7770ed4734d76472eb9b630515553be84dfa4ad8c6f200ab098e5709966cc659938082a2955cd740"
    my_var_b_pt = bytes.fromhex(my_var_plaintext)
    my_var_b_ct = bytes.fromhex(my_var_ciphertext)
    my_var_b_ks = b""

    ### Get the used keystream by XOR the plaintext and ciphertext
    for i in range(len(my_var_b_pt)):
        my_var_b_ks += int.to_bytes(my_var_b_pt[i] ^ my_var_b_ct[i])

    ### Let's map out the potential values for each key
    my_var_potential_values = ["" for _ in range(32)]
    for i, j in my_var_map:
        my_var_k = my_var_b_ks[i]

        ### Again, if it is above 0x80, let's XOR it back
        if my_var_k & 0x80:
            my_var_k ^=0xff

        ### keystream has to be a printable chr
        if 0x80 > my_var_k > 0x20:
            my_var_potential_values[j] += chr(my_var_k)

    ### Print out all the potential values, you will be able to make out the flag
    for i in my_var_potential_values:
        print(i)

    ### To improve the result, you can use several different KEY to filter out useless map values.