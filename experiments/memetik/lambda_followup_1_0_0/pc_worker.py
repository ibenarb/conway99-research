"""Run the frozen worker with the narrowly specified PC engine."""
import boot
import engine
from pc_engine import PCEngine
engine.Engine = PCEngine
import worker
if __name__ == "__main__":
    worker.main()
