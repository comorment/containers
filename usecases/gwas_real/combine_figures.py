import matplotlib.pyplot as plt
import json
plt.figure(figsize=(15,10))
fnames = ['run1_height.plink2', 'run2_height.regenie', 'run5_height.plink2', 'run6_height.regenie']
labels = ['plink2 (hard calls)', 'regenie (hard calls)', 'plink2 (dosages)', 'regenie (dosages)']
for fname, label in zip(fnames, labels):
    j=json.loads(open('out/{}.gz.qq.png.json'.format(fname)).read())
    plt.plot(j['x'], j['y'], label=label)
plt.legend()
plt.plot([0, 7], [0, 7], 'k--')
plt.title('height, n=56211')
plt.savefig('out/height.qq.png')

plt.figure(figsize=(15,10/3))
fnames = ['run3_{}.plink2', 'run4_{}.regenie', 'run7_{}.plink2', 'run8_{}.regenie']
for index, trait, ncase in [(1, 'AnyFdep', 3536), (2, 'AnyF32', 2477), (3, 'AnyF33', 1623)]:
    plt.subplot(1,3,index)
    for fname, label in zip(fnames, labels):
        j=json.loads(open('out/{}.gz.qq.png.json'.format(fname.format(trait))).read())
        plt.plot(j['x'], j['y'], label=label)
    if index==1: plt.legend()
    plt.plot([0, 7], [0, 7], 'k--')
    plt.title('{}, n={}'.format(trait, ncase))
plt.savefig('out/dep.qq.png')
    
