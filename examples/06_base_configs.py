"""We can integrate `dcargs.cli()` into common configuration patterns: here, we select
one of multiple possible base configurations, and then use the CLI to either override
(existing) or fill in (missing) values.

Usage:
`BASE_CONFIG=small python ./06_base_configs.py --help`
`BASE_CONFIG=small python ./06_base_configs.py --seed 94720`
`BASE_CONFIG=big python ./06_base_configs.py --help`
`BASE_CONFIG=big python ./06_base_configs.py --seed 94720`
"""

import dataclasses
import os
from typing import Literal, Tuple, Union

import dcargs


@dataclasses.dataclass
class AdamOptimizer:
    # Adam learning rate.
    learning_rate: float = 1e-3

    # Moving average parameters.
    betas: Tuple[float, float] = (0.9, 0.999)


@dataclasses.dataclass
class SgdOptimizer:
    # SGD learning rate.
    learning_rate: float = 3e-4


@dataclasses.dataclass(frozen=True)
class ExperimentConfig:
    # Dataset to run experiment on.
    dataset: Literal["mnist", "imagenet-50"]

    # Optimizer parameters.
    optimizer: Union[AdamOptimizer, SgdOptimizer]

    # Model size.
    num_layers: int
    units: int

    # Batch size.
    batch_size: int

    # Total number of training steps.
    train_steps: int

    # Random seed. This is helpful for making sure that our experiments are all
    # reproducible!
    seed: int


# Note that we could also define this library using separate YAML files (similar to
# `config_path`/`config_name` in Hydra), but staying in Python enables seamless type
# checking + IDE support.
base_config_library = {
    "small": ExperimentConfig(
        dataset="mnist",
        optimizer=SgdOptimizer(),
        batch_size=2048,
        num_layers=4,
        units=64,
        train_steps=30_000,
        # The dcargs.MISSING sentinel allows us to specify that the seed should have no
        # default, and needs to be populated from the CLI.
        seed=dcargs.MISSING,
    ),
    "big": ExperimentConfig(
        dataset="imagenet-50",
        optimizer=AdamOptimizer(),
        batch_size=32,
        num_layers=8,
        units=256,
        train_steps=100_000,
        seed=dcargs.MISSING,
    ),
}

if __name__ == "__main__":
    # Get base configuration name from environment.
    base_config_name = os.environ.get("BASE_CONFIG")
    if base_config_name is None or base_config_name not in base_config_library:
        raise SystemExit(
            f"BASE_CONFIG should be set to one of {tuple(base_config_library.keys())}"
        )

    # Get base configuration from our library, and use it for default CLI parameters.
    base_config = base_config_library[base_config_name]
    config = dcargs.cli(
        ExperimentConfig,
        default_instance=base_config,
        # `avoid_subparsers` will avoid making a subparser for unions when a default is
        # provided; in this case, it makes our CLI less expressive (cannot switch
        # away from the base optimizer types), but easier to use.
        avoid_subparsers=True,
    )
    print(config)
