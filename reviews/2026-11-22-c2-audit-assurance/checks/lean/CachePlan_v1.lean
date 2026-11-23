import Cache.Hashing

open Cache IO Hashing in
def main (args : List String) : IO Unit := do
    CacheM.run do
        let roots ← parseArgs args
        if roots.isEmpty then
            throw <| IO.userError "Explicit module roots required"
        let memo ← getHashMemo roots
        let hashes ← memo.filterByRootModules roots.keys
        let config ← mkLeanTarConfig hashes
        IO.println s!"CONFIG {Lean.Json.compress (.arr config)}"
        for (name, hash) in hashes.toArray do
            IO.println s!"MODULE {name} {hash.asLTar}"
        IO.println s!"TOTAL {hashes.size}"
