# Fleet public keys

Drop `.pub` files here (one per trusted machine, e.g. `laptop.pub`,
`coralreef.pub`); `provision.yml` installs every key in this directory into
`authorized_keys` on every node, additively.

Public keys only — they are non-secret by design. Private keys never enter the
repo. See `deploy/PROVISIONING.md` for the key scheme and recovery rationale.
