#!/usr/bin/env python3
"""
Extended sample analysis: ZLB structural break in regime-dependent sentiment.

Key finding: The interaction between monetary policy shocks and sentiment
is significant ONLY in the ZLB+Post era (2008-2022), not in the Pre-ZLB era (1995-2008).
This supports the forward guidance channel: path shocks matter only when
the Fed relies on language (FG) rather than rate changes to signal policy.

Data: fomc_master_extended.csv (N=164, 1995-2022)
Shocks: Acosta (2022) replication of GSS target/path shocks
Sentiment: CB V2 (Correa et al. 2021 dictionary)
Regime: Master classification (2006-2022) + FRED rate changes (1995-2005)
"""
import pandas as pd, numpy as np
import statsmodels.api as sm
from scipy import stats

def run_reg(data, y, X_cols, hac_lags=4):
    """OLS with HAC standard errors."""
    X = sm.add_constant(data[X_cols].values)
    model = sm.OLS(data[y].values, X).fit(cov_type='HAC', cov_kwds={'maxlags': hac_lags})
    result = {'N': int(model.nobs), 'R2': model.rsquared, 'R2_adj': model.rsquared_adj}
    for i, col in enumerate(['const'] + X_cols):
        sig = '***' if model.pvalues[i]<0.001 else '**' if model.pvalues[i]<0.01 else '*' if model.pvalues[i]<0.05 else ''
        result[col] = {'beta': model.params[i], 'se': model.bse[i], 't': model.tvalues[i], 
                       'p': model.pvalues[i], 'sig': sig}
    return result

def permutation_test(data, y, X_cols, test_col_idx, n_perm=5000, seed=42):
    """Permutation test by shuffling the direction variable."""
    np.random.seed(seed)
    X = sm.add_constant(data[X_cols].values)
    y_arr = data[y].values
    model = sm.OLS(y_arr, X).fit(cov_type='HAC', cov_kwds={'maxlags':4})
    obs_t = model.tvalues[test_col_idx]
    
    # Find which column is 'direction' to shuffle
    dir_idx = X_cols.index('direction')
    
    t_perm = []
    for _ in range(n_perm):
        dir_perm = data['direction'].values.copy()
        np.random.shuffle(dir_perm)
        X_perm = X.copy()
        # Update direction and interaction columns
        for j, col in enumerate(X_cols):
            if col == 'direction':
                X_perm[:, j+1] = dir_perm
            elif col == 'target_x_dir':
                X_perm[:, j+1] = data['target'].values * dir_perm
            elif col == 'path_x_dir':
                X_perm[:, j+1] = data['path'].values * dir_perm
        model_perm = sm.OLS(y_arr, X_perm).fit()
        t_perm.append(model_perm.tvalues[test_col_idx])
    
    p_perm = np.mean(np.abs(t_perm) >= np.abs(obs_t))
    return obs_t, p_perm

def wild_bootstrap(data, y, X_cols, restrict_cols, test_col_idx, n_boot=5000, seed=42):
    """Wild bootstrap under H0 (restricted model excludes test variable)."""
    np.random.seed(seed)
    X_full = sm.add_constant(data[X_cols].values)
    X_restr = sm.add_constant(data[restrict_cols].values)
    y_arr = data[y].values
    
    model_restr = sm.OLS(y_arr, X_restr).fit(cov_type='HAC', cov_kwds={'maxlags':4})
    model_full = sm.OLS(y_arr, X_full).fit(cov_type='HAC', cov_kwds={'maxlags':4})
    obs_t = model_full.tvalues[test_col_idx]
    
    t_boot = []
    for _ in range(n_boot):
        signs = np.random.choice([-1, 1], size=len(y_arr))
        y_boot = model_restr.fittedvalues + signs * model_restr.resid
        model_boot = sm.OLS(y_boot, X_full).fit()
        t_boot.append(model_boot.tvalues[test_col_idx])
    
    se_boot = np.std(t_boot)
    p_boot = np.mean(np.abs(t_boot) >= np.abs(obs_t))
    return obs_t, p_boot, se_boot

def monte_carlo_size(data, y, X_cols_base, X_cols_full, test_col_idx, n_sim=2000, seed=42):
    """Monte Carlo size test: rejection rate under H0."""
    np.random.seed(seed)
    X_base = sm.add_constant(data[X_cols_base].values)
    X_full = sm.add_constant(data[X_cols_full].values)
    y_arr = data[y].values
    
    model_base = sm.OLS(y_arr, X_base).fit(cov_type='HAC', cov_kwds={'maxlags':4})
    sigma = np.std(model_base.resid)
    
    reject_05 = 0
    for _ in range(n_sim):
        y_h0 = model_base.fittedvalues + np.random.normal(0, sigma, len(y_arr))
        model_s = sm.OLS(y_h0, X_full).fit(cov_type='HAC', cov_kwds={'maxlags':4})
        if model_s.pvalues[test_col_idx] < 0.05:
            reject_05 += 1
    
    return reject_05 / n_sim

def leave_one_regime_out(data, y, X_cols):
    """Test robustness by dropping each regime."""
    results = {}
    for drop in ['hike', 'cut', 'unchanged']:
        sub = data[data['regime'] != drop].copy()
        r = run_reg(sub, y, X_cols)
        results[drop] = {'N': r['N'], 
                         'target_x_dir_t': r['target_x_dir']['t'],
                         'path_x_dir_t': r['path_x_dir']['t']}
    return results

# ============================================================
# Main analysis
# ============================================================
if __name__ == '__main__':
    df = pd.read_csv('data/fomc_master_extended.csv')
    df['fomc'] = pd.to_datetime(df['fomc'])
    
    X_cols = ['target', 'path', 'direction', 'target_x_dir', 'path_x_dir']
    
    print("="*70)
    print("EXTENDED SAMPLE ANALYSIS: ZLB Structural Break")
    print("="*70)
    
    # 1. Full extended sample (N=164)
    print(f"\n1. Full extended sample (N={len(df)})")
    r = run_reg(df, 'cb_score_v2', X_cols)
    print(f"   target×direction: t={r['target_x_dir']['t']:.2f}{r['target_x_dir']['sig']}")
    print(f"   path×direction:   t={r['path_x_dir']['t']:.2f}{r['path_x_dir']['sig']}")
    print(f"   R²={r['R2']:.4f}")
    
    # 2. By era
    for era in ['pre_zlb', 'zlb_post']:
        sub = df[df['era'] == era]
        print(f"\n2. {era} (N={len(sub)})")
        r = run_reg(sub, 'cb_score_v2', X_cols)
        print(f"   target×direction: t={r['target_x_dir']['t']:.2f}{r['target_x_dir']['sig']}")
        print(f"   path×direction:   t={r['path_x_dir']['t']:.2f}{r['path_x_dir']['sig']}")
        print(f"   R²={r['R2']:.4f}")
    
    # 3. Permutation test (ZLB+Post)
    zlb = df[df['era'] == 'zlb_post']
    print(f"\n3. Permutation test (ZLB+Post, N={len(zlb)})")
    for name, idx in [('target×direction', 4), ('path×direction', 5)]:
        obs_t, p_perm = permutation_test(zlb, 'cb_score_v2', X_cols, idx)
        print(f"   {name}: t={obs_t:.2f}, Permutation p={p_perm:.4f}")
    
    # 4. Wild Bootstrap (ZLB+Post)
    print(f"\n4. Wild Bootstrap (ZLB+Post, N={len(zlb)})")
    for name, idx, restrict in [
        ('target×direction', 4, ['target', 'path', 'direction', 'path_x_dir']),
        ('path×direction', 5, ['target', 'path', 'direction', 'target_x_dir'])
    ]:
        obs_t, p_boot, se_boot = wild_bootstrap(zlb, 'cb_score_v2', X_cols, restrict, idx)
        print(f"   {name}: t={obs_t:.2f}, Bootstrap p={p_boot:.4f}")
    
    # 5. Monte Carlo size (ZLB+Post)
    print(f"\n5. Monte Carlo size (ZLB+Post, N={len(zlb)})")
    size = monte_carlo_size(zlb, 'cb_score_v2', 
                            ['target', 'path', 'direction'], X_cols, 5)
    print(f"   HAC rejection rate at 5%: {size:.3f}")
    
    # 6. Leave-one-regime-out (ZLB+Post)
    print(f"\n6. Leave-one-regime-out (ZLB+Post)")
    loro = leave_one_regime_out(zlb, 'cb_score_v2', X_cols)
    for drop, vals in loro.items():
        print(f"   Drop {drop} (N={vals['N']}): target×dir t={vals['target_x_dir_t']:.2f}, path×dir t={vals['path_x_dir_t']:.2f}")
    
    # 7. Original N=131 for comparison
    master = pd.read_csv('data/fomc_master_v3.csv')
    master['fomc'] = pd.to_datetime(master['fomc'])
    master['direction'] = master['regime'].map({'hike': 1, 'unchanged': 0, 'cut': -1})
    master['target_x_dir'] = master['target'] * master['direction']
    master['path_x_dir'] = master['path'] * master['direction']
    
    print(f"\n7. Original sample (N={len(master)}) for comparison")
    r = run_reg(master, 'cb_score_v2', X_cols)
    print(f"   target×direction: t={r['target_x_dir']['t']:.2f}{r['target_x_dir']['sig']}")
    print(f"   path×direction:   t={r['path_x_dir']['t']:.2f}{r['path_x_dir']['sig']}")
    
    print(f"\n{'='*70}")
    print("SUMMARY: ZLB structural break")
    print("="*70)
    print("""
    Pre-ZLB (1995-2008): No regime-dependent sentiment response
    ZLB+Post (2008-2022): Significant target×direction and path×direction
    
    Interpretation: Forward guidance makes path shocks relevant for
    sentiment only in the ZLB era, when the Fed relies on language
    rather than rate changes to signal future policy.
    """)
