from pathlib import Path
from rigagent.vectorstore import texts_to_vectorstore

texts_to_vectorstore(Path("./rigdata/rig_manual_mgear_biped.txt"))