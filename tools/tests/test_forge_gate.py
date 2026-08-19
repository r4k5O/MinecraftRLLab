from tools.forge_gate import DEFAULT_FORGE_KEY, build_token, resolve_mode, select_forge_key


def test_missing_secret_is_always_normal():
    assert resolve_mode('X-MCRL-Forge: deadbeef', '', 'abc123') == 'normal'


def test_normal_commit_is_normal():
    assert resolve_mode('feat: improve tutorial', 'super-secret', 'tree123') == 'normal'


def test_wrong_token_is_normal():
    message = 'feat: build\n\nX-MCRL-Forge: ' + ('0' * 64)
    assert resolve_mode(message, 'super-secret', 'tree123') == 'normal'


def test_valid_tree_bound_hmac_enables_full_source():
    token = build_token('super-secret', 'tree123')
    message = f'feat: build\n\nX-MCRL-Forge: {token}'
    assert resolve_mode(message, 'super-secret', 'tree123') == 'full-source'


def test_token_is_bound_to_exact_tree():
    token = build_token('super-secret', 'tree123')
    message = f'X-MCRL-Forge: {token}'
    assert resolve_mode(message, 'super-secret', 'tree124') == 'normal'


def test_default_forge_key_is_used_when_github_secret_is_missing():
    assert select_forge_key('') == DEFAULT_FORGE_KEY
    token = build_token(DEFAULT_FORGE_KEY, 'tree-default')
    message = f'X-MCRL-Forge: {token}'
    assert resolve_mode(message, select_forge_key(''), 'tree-default') == 'full-source'


def test_github_secret_overrides_default_forge_key():
    custom = 'owner-private-forge-key'
    assert select_forge_key(custom) == custom
    default_token = build_token(DEFAULT_FORGE_KEY, 'tree-secret')
    custom_token = build_token(custom, 'tree-secret')
    assert resolve_mode(f'X-MCRL-Forge: {default_token}', select_forge_key(custom), 'tree-secret') == 'normal'
    assert resolve_mode(f'X-MCRL-Forge: {custom_token}', select_forge_key(custom), 'tree-secret') == 'full-source'
