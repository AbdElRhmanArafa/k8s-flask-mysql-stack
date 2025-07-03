# MySQL Helm Chart - Dynamic NFS Storage

This Helm chart deploys a MySQL database with dynamic NFS storage provisioning.

## Overview

The chart uses a dynamic provisioner for NFS storage, which automatically creates
PersistentVolumes when PersistentVolumeClaims are created. This eliminates the need
for manually creating PersistentVolumes.

## Prerequisites

- Kubernetes cluster
- NFS server accessible from the cluster
- NFS subdir external provisioner installed (optional, see below)

## Installation

### 1. Ensure NFS Provisioner is Installed

Before installing the MySQL chart, make sure the NFS provisioner is installed:

```bash
# Check if the storage class exists
kubectl get storageclass nfs-client

# If not found, install the provisioner
./scripts/install-nfs-provisioner.sh --server 192.168.121.12 --path /export/nfs
```

### 2. Synchronize Configuration (Optional)

To ensure all NFS configuration is consistent:

```bash
./scripts/sync-nfs-config.sh
```

This will update the chart values to match your NFS server configuration.

### 3. Install the MySQL Chart

```bash
helm install mysql kubernetes/helm/mysql
```

## Configuration

The main configuration for storage is in `values.yaml`:

```yaml
pv:
  enabled: true
  size: 5Gi
  accessMode: ReadWriteOnce
  createStorageClass: false  # Set to true if you want to create a StorageClass
  storageClass: "nfs-client"  # Must match your provisioner's storage class
  nfs:
    server: "192.168.121.12"
    path: "/export/nfs"
    readOnly: false
    reclaimPolicy: Delete
    volumeBindingMode: Immediate
    allowVolumeExpansion: true
```

## Troubleshooting

If PVCs remain in "Pending" status:

1. Check if the storage class exists:

   ```bash
   kubectl get storageclass nfs-client
   ```

2. If not found, install the NFS provisioner:

   ```bash
   ./scripts/install-nfs-provisioner.sh
   ```

3. Verify NFS server is accessible from the cluster

## How Dynamic Provisioning Works

1. PVC requests storage from StorageClass "nfs-client"
2. NFS provisioner creates a directory on the NFS server
3. Provisioner creates a PV pointing to that directory
4. PV is bound to the PVC
5. Pod mounts the PVC
