import inspect
import os
import sys
from pathlib import Path

import pytest

# Add ricer-mcp root so provider_runtime and features can be imported directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from feature import Feature, FeatureType
from provider_runtime import ensure_provider_paths

# Ensure provider paths are configured (kde-plasma-6 features package is found)
ensure_provider_paths()

import features


def _sample_value(annotation):
    if annotation in (bool,):
        return True
    if annotation in (int,):
        return 1
    if annotation in (float,):
        return 1.0
    if annotation in (str,):
        return "/tmp/test"
    if annotation in (dict,):
        return {}
    if annotation in (list,):
        return []
    if annotation in (tuple,):
        return ()
    return "test"


def test_each_feature_module_contract():
    """Each feature module should expose a Feature instance and the required APIs."""
    assert hasattr(features, "_FEATURE_MODULES")
    assert features._FEATURE_MODULES, "No feature modules were found"

    for module in features._FEATURE_MODULES:
        assert hasattr(module, "feature"), f"{module.__name__} is missing module.feature"
        feature = module.feature
        assert isinstance(feature, Feature), f"{module.__name__}.feature is not a Feature instance"
        assert feature.type in FeatureType

        for api in ("set", "get", "register_tool", "register_resource"):
            assert callable(getattr(feature, api, None)), f"{module.__name__}.feature.{api} is not callable"


def test_register_all_features_without_errors():
    """Registering all tools and resources should not crash."""

    class DummyMCP:
        def tool(self):
            def decorator(func):
                return func
            return decorator

        def resource(self, _uri):
            def decorator(func):
                return func
            return decorator

    class DummyChangeset:
        def add(self, **kwargs):
            return kwargs

    dummy_mcp = DummyMCP()
    dummy_changeset = DummyChangeset()

    # Should not raise any errors
    features.register_all(dummy_mcp, dummy_changeset)


@pytest.mark.parametrize("module", list(features._FEATURE_MODULES))
def test_feature_set_get_cycle_for_each_module(module, monkeypatch, tmp_path):
    """Invoke set/get for each feature with mocked side effects."""
    # Isolate environment to a temp home for file operations.
    monkeypatch.setenv("HOME", str(tmp_path))

    # Patch write routines if exposed at module scope
    if hasattr(module, "write_kde_configs"):
        monkeypatch.setattr(module, "write_kde_configs", lambda *args, **kwargs: True)
    if hasattr(module, "write_kde_config"):
        monkeypatch.setattr(module, "write_kde_config", lambda *args, **kwargs: True)
    if hasattr(module, "run_plasma_script"):
        monkeypatch.setattr(module, "run_plasma_script", lambda *a, **k: True)

    # Patch util read adapters used by get() paths
    try:
        import utils.read.kreadconfig as kreadconfig

        monkeypatch.setattr(kreadconfig, "read_kde_config", lambda *args, **kwargs: "true")
        monkeypatch.setattr(
            kreadconfig,
            "read_kde_configs",
            lambda *args, **kwargs: {"enabled": "true", "theme": "ocean", "idleTime": "60000"},
        )
    except Exception:
        pass

    try:
        import utils.kde_config_reader as kde_config_reader

        monkeypatch.setattr(kde_config_reader, "read_current_wallpaper", lambda: "/tmp/dummy_wallpaper.jpg")
        monkeypatch.setattr(kde_config_reader, "read_kde_config", lambda *args, **kwargs: "" )
        monkeypatch.setattr(kde_config_reader, "read_kde_configs", lambda *args, **kwargs: {})
    except Exception:
        pass

    feature = module.feature

    # Build arguments for set() using required positional parameters
    set_signature = inspect.signature(feature.set)
    kwargs = {}
    for name, param in set_signature.parameters.items():
        if param.default is inspect.Parameter.empty:
            kwargs[name] = _sample_value(param.annotation)

    try:
        set_result = feature.set(**kwargs)
    except TypeError as e:
        # Some features may require complex values that are difficult to infer; skip those cases.
        pytest.skip(f"Skipping set() for {module.__name__}: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected failure in {module.__name__}.feature.set: {e}")

    assert isinstance(set_result, bool)

    try:
        get_result = feature.get()
    except Exception as e:
        pytest.fail(f"Unexpected failure in {module.__name__}.feature.get: {e}")

    assert isinstance(get_result, dict)
