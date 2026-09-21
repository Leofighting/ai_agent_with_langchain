# -*- coding: utf-8 -*-
"""
@Time : 2026/9/21 9:10
@Author: janic
@File: file_saver.py
"""
import json
import os
from pathlib import Path
from typing import Optional, Sequence, Tuple, Any
import pickle, base64

from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver, CheckpointTuple, Checkpoint, CheckpointMetadata, \
    ChannelVersions

from app.agent.model.qwen import llm_qwen
from app.agent.tools.file_tools import file_tools


class FileSaver(BaseCheckpointSaver[str]):
    def __init__(self,
                 base_path=r"D:\code_project\ai_agent_with_langchain\.temp\checkpoint\file_save"):
        super().__init__()
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def _get_checkpoint_path(self, thread_id, checkpoint_id):
        dir_path = os.path.join(self.base_path, thread_id)
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, checkpoint_id + ".json")
        return file_path

    def _serialize_checkpoint(self, data) -> str:
        pickled_data = pickle.dumps(data)
        return base64.b64encode(pickled_data).decode()

    def _deserialize_data(self, data):
        decoded = base64.b64decode(data)
        return pickle.loads(decoded)

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]['thread_id']
        # checkpoint_id = config['configurable'].get("checkpoint_id")

        dir_path = os.path.join(self.base_path, thread_id)
        checkpoint_files = list(Path(dir_path).glob("*.json"))
        checkpoint_files.sort(key=lambda x: x.stem, reverse=True)
        if len(checkpoint_files) > 0:
            latest_checkpoint = checkpoint_files[0]
            checkpoint_id = latest_checkpoint.stem
            checkpoint_file_path = self._get_checkpoint_path(thread_id, checkpoint_id)

            with open(checkpoint_file_path, "r", encoding="utf-8") as checkpoint_file:
                data = json.load(checkpoint_file)
            checkpoint = self._deserialize_data(data["checkpoint"])
            metadata = self._deserialize_data(data["metadata"])

            return CheckpointTuple(
                config={
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_id": checkpoint_id
                    }
                },
                checkpoint=checkpoint,
                metadata=metadata
            )
        else:
            return None

    def put(self,
            config: RunnableConfig,
            checkpoint: Checkpoint,
            metadata: CheckpointMetadata,
            new_versions: ChannelVersions) -> RunnableConfig:
        thread_id = config["configurable"]["thread_id"]

        checkpoint_id = checkpoint['id']
        checkpoint_path = self._get_checkpoint_path(thread_id, checkpoint_id)

        checkpoint_data = {
            "checkpoint": self._serialize_checkpoint(checkpoint),
            "metadata": self._serialize_checkpoint(metadata)
        }

        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)

        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id
            }
        }

    def put_writes(self,
                   config: RunnableConfig,
                   writes: Sequence[Tuple[str, Any]],
                   task_id: str,
                   task_path: str="") -> None:
        print("put_writes")


if __name__ == '__main__':
    memory = FileSaver()
    agent = create_agent(
            model=llm_qwen,
            tools=file_tools,
            checkpointer=memory,
            debug=False
        )
    config1 = RunnableConfig(configurable={"thread_id": 2})
    while True:
        user_input = input("用户：")
        if user_input == "exit":
            break
        res = agent.invoke(input={"messages": user_input}, config=config1)
        print(res["messages"][-1].content)
