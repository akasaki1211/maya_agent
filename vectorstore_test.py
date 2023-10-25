from pathlib import Path

from mayaagent.vectorstore import VectorStore

# create vectorstore
#vec_store = VectorStore()
#vec_store.txt_to_vectorstore(Path("./rigdata/rig_manual_mgear_biped.txt"))

# load vectorstore, and query
vec_store = VectorStore(Path("./rigdata/rig_manual_mgear_biped.json"))
search_result = vec_store.similarity_search("腕のIKFK切り替え")
for sr in search_result:
    print(sr[0]["content"])
    print("score:", sr[1])
    print('--'*30)