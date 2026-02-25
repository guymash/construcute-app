from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest


def _has_docker() -> bool:
  return subprocess.call(
      ["docker", "version"],
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL,
  ) == 0


def _wait_for_port(host: str, port: int, timeout: float = 30.0) -> None:
  deadline = time.time() + timeout
  while time.time() < deadline:
      with socket.socket() as sock:
          sock.settimeout(1.0)
          try:
              sock.connect((host, port))
              return
          except OSError:
              time.sleep(0.5)
  raise TimeoutError(f"Timed out waiting for {host}:{port}")


@pytest.mark.integration
def test_migrations_apply_on_fresh_database() -> None:
  if not _has_docker():
      pytest.skip("Docker not available, skipping integration test")

  container_name = "constructure-migrations-test-db"
  db_port = 55432

  subprocess.run(
      [
          "docker",
          "rm",
          "-f",
          container_name,
      ],
      check=False,
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL,
  )

  try:
      subprocess.run(
          [
              "docker",
              "run",
              "-d",
              "--name",
              container_name,
              "-e",
              "POSTGRES_USER=app",
              "-e",
              "POSTGRES_PASSWORD=app",
              "-e",
              "POSTGRES_DB=app",
              "-p",
              f"{db_port}:5432",
              "postgres:16",
          ],
          check=True,
      )

      _wait_for_port("127.0.0.1", db_port, timeout=60.0)

      env = os.environ.copy()
      env["DATABASE_URL"] = (
          f"postgresql+psycopg://app:app@127.0.0.1:{db_port}/app"
      )

      api_dir = Path(__file__).resolve().parents[1]

      subprocess.run(
          [
              sys.executable,
              "-m",
              "alembic",
              "-c",
              "alembic.ini",
              "upgrade",
              "head",
          ],
          check=True,
          cwd=api_dir,
          env=env,
      )
  finally:
      subprocess.run(
          [
              "docker",
              "rm",
              "-f",
              container_name,
          ],
          check=False,
          stdout=subprocess.DEVNULL,
          stderr=subprocess.DEVNULL,
      )

