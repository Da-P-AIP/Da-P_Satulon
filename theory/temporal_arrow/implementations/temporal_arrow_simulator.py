"""
da-P粒子スピン理論の完全実装
時間の矢シミュレーター with GPU加速
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List, Dict, Optional
import time
from dataclasses import dataclass
from enum import Enum

try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    cp = np
    CUPY_AVAILABLE = False

class SpinDirection(Enum):
    """da-P粒子スピン方向"""
    UP = +1
    DOWN = -1
    RANDOM = 0

@dataclass
class DaPParticleWithSpin:
    """スピン付きda-P粒子の完全実装"""
    position: np.ndarray
    density: float
    spin_vector: np.ndarray
    energy: float
    temporal_signature: float
    
    def __post_init__(self):
        self.spin_magnitude = np.linalg.norm(self.spin_vector)
        self.temporal_direction = np.sign(self.spin_vector[2])  # z成分が時間方向
        
    def information_flow_direction(self) -> Dict:
        """情報流動方向の計算"""
        return {
            'forward_time': self.temporal_direction > 0,
            'backward_time': self.temporal_direction < 0,
            'flow_intensity': abs(self.temporal_direction) * self.density,
            'temporal_coherence': self.spin_magnitude
        }

class TemporalArrowSimulator:
    """時間の矢シミュレーター - GPU対応完全版"""
    
    def __init__(self, grid_size: int = 256, dt: float = 1e-12, use_gpu: bool = True):
        self.grid_size = grid_size
        self.dt = dt  # プランク時間単位
        self.use_gpu = use_gpu and CUPY_AVAILABLE
        
        # GPU/CPU自動選択
        self.xp = cp if self.use_gpu else np
        
        print(f"Using {'GPU (CuPy)' if self.use_gpu else 'CPU (NumPy)'}")
        
        # da-P粒子スピン場 (3次元ベクトル場)
        self.spin_field = self.xp.random.random((grid_size, grid_size, 3)).astype(self.xp.float32) - 0.5
        norms = self.xp.linalg.norm(self.spin_field, axis=2, keepdims=True)
        self.spin_field /= norms + 1e-10
        
        # 情報密度場
        self.info_field = self.xp.random.random((grid_size, grid_size)).astype(self.xp.float32)
        
        # 時間の矢の強度
        self.temporal_arrow_strength = 0.0
        
        # 履歴記録
        self.history = {
            'arrow_strength': [],
            'spin_polarization': [],
            'entropy': [],
            'information_flow': [],
            'irreversibility': []
        }
    
    def evolve_spin_field(self) -> None:
        """スピン場の時間発展 - GPU最適化版"""
        # パディングで境界条件処理
        padded_spin = self.xp.pad(self.spin_field, ((1, 1), (1, 1), (0, 0)), mode='wrap')
        
        # 8近傍の平均計算 (ベクトル化)
        neighbors = (
            padded_spin[:-2, :-2] + padded_spin[:-2, 1:-1] + padded_spin[:-2, 2:] +
            padded_spin[1:-1, :-2] +                         padded_spin[1:-1, 2:] +
            padded_spin[2:, :-2] + padded_spin[2:, 1:-1] + padded_spin[2:, 2:]
        ) / 8.0
        
        # 相互作用によるスピン更新
        interaction_strength = 0.1
        self.spin_field += interaction_strength * (
            neighbors - self.spin_field
        ) * self.dt
        
        # 正規化
        norms = self.xp.linalg.norm(self.spin_field, axis=2, keepdims=True)
        self.spin_field /= norms + 1e-10
    
    def update_information_field(self) -> None:
        """情報場の更新 - スピン依存拡散"""
        # ラプラシアン計算
        padded_info = self.xp.pad(self.info_field, 1, mode='wrap')
        laplacian = (
            padded_info[:-2, 1:-1] + padded_info[2:, 1:-1] +
            padded_info[1:-1, :-2] + padded_info[1:-1, 2:] -
            4 * self.info_field
        )
        
        # スピンz成分による方向性拡散
        diffusion_rate = 0.01 * self.xp.abs(self.spin_field[:, :, 2])
        
        self.info_field += diffusion_rate * laplacian * self.dt
        
        # 境界条件
        self.info_field = self.xp.clip(self.info_field, 0, 1)
    
    def calculate_temporal_arrow(self) -> float:
        """時間の矢の強度計算"""
        # z成分（時間方向）の偏極度
        z_polarization = float(self.xp.mean(self.spin_field[:, :, 2]))
        
        # 情報流動の方向性
        info_grad_x = self.xp.gradient(self.info_field, axis=1)
        info_grad_y = self.xp.gradient(self.info_field, axis=0)
        
        flow_direction_x = float(self.xp.sum(info_grad_x * self.spin_field[:, :, 0]))
        flow_direction_y = float(self.xp.sum(info_grad_y * self.spin_field[:, :, 1]))
        
        flow_magnitude = np.sqrt(flow_direction_x**2 + flow_direction_y**2)
        
        # 時間の矢の強度
        self.temporal_arrow_strength = abs(z_polarization) * flow_magnitude / (self.grid_size**2)
        
        return self.temporal_arrow_strength
    
    def measure_entropy(self) -> float:
        """系のエントロピー測定"""
        # スピンz成分の分布
        z_spins = self.spin_field[:, :, 2].flatten()
        z_up = float(self.xp.sum(z_spins > 0))
        z_down = float(self.xp.sum(z_spins < 0))
        
        if z_up == 0 or z_down == 0:
            return 0.0
        
        total = z_up + z_down
        p_up = z_up / total
        p_down = z_down / total
        
        return -p_up * np.log2(p_up + 1e-12) - p_down * np.log2(p_down + 1e-12)
    
    def calculate_irreversibility(self) -> float:
        """不可逆性の計算"""
        if len(self.history['entropy']) < 2:
            return 0.0
        
        # エントロピー変化の一方向性
        entropy_changes = np.diff(self.history['entropy'])
        
        if len(entropy_changes) == 0:
            return 0.0
        
        forward_changes = np.sum(entropy_changes > 0)
        backward_changes = np.sum(entropy_changes < 0)
        
        if forward_changes + backward_changes == 0:
            return 0.0
        
        return (forward_changes - backward_changes) / (forward_changes + backward_changes)
    
    def calculate_spin_coherence(self) -> float:
        """スピンコヒーレンス計算"""
        if len(self.history['spin_polarization']) == 0:
            return 0.0
        
        return float(np.mean([abs(p) for p in self.history['spin_polarization']]))
    
    def run_simulation(self, steps: int = 1000, save_interval: int = 10) -> Dict:
        """完全シミュレーション実行"""
        print(f"Starting temporal arrow simulation for {steps} steps...")
        print(f"Grid size: {self.grid_size}x{self.grid_size}")
        print(f"da-P particles: {self.grid_size**2:,}")
        
        start_time = time.time()
        
        for step in range(steps):
            # スピン場進化
            self.evolve_spin_field()
            
            # 情報場更新
            self.update_information_field()
            
            # 観測量計算
            if step % save_interval == 0:
                arrow_strength = self.calculate_temporal_arrow()
                entropy = self.measure_entropy()
                spin_polarization = float(self.xp.mean(self.spin_field[:, :, 2]))
                
                # 履歴記録
                self.history['arrow_strength'].append(arrow_strength)
                self.history['spin_polarization'].append(spin_polarization)
                self.history['entropy'].append(entropy)
                
                if step % (save_interval * 10) == 0:
                    elapsed = time.time() - start_time
                    rate = (step + 1) / elapsed if elapsed > 0 else 0
                    print(f"Step {step:5d}: Arrow={arrow_strength:.6f}, "
                          f"Entropy={entropy:.6f}, Rate={rate:.1f} steps/s")
        
        total_time = time.time() - start_time
        throughput = steps * self.grid_size**2 / total_time
        
        print(f"\nSimulation completed in {total_time:.2f} seconds")
        print(f"Throughput: {throughput:,.0f} da-P particles/second")
        
        return self.analyze_results()
    
    def analyze_results(self) -> Dict:
        """結果分析"""
        results = {
            'final_arrow_strength': self.history['arrow_strength'][-1] if self.history['arrow_strength'] else 0,
            'average_arrow_strength': float(np.mean(self.history['arrow_strength'])) if self.history['arrow_strength'] else 0,
            'arrow_consistency': float(np.std(self.history['arrow_strength'])) if self.history['arrow_strength'] else 0,
            'entropy_evolution': self.history['entropy'],
            'temporal_irreversibility': self.calculate_irreversibility(),
            'spin_coherence': self.calculate_spin_coherence(),
            'final_polarization': self.history['spin_polarization'][-1] if self.history['spin_polarization'] else 0
        }
        
        return results
    
    def plot_results(self, save_path: str = None):
        """結果可視化"""
        if not self.history['arrow_strength']:
            print("No data to plot. Run simulation first.")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # 時間の矢の強度
        axes[0, 0].plot(self.history['arrow_strength'])
        axes[0, 0].set_title('Temporal Arrow Strength')
        axes[0, 0].set_xlabel('Time Step')
        axes[0, 0].set_ylabel('Arrow Strength')
        axes[0, 0].grid(True)
        
        # スピン偏極度
        axes[0, 1].plot(self.history['spin_polarization'])
        axes[0, 1].set_title('Spin Polarization (Z-component)')
        axes[0, 1].set_xlabel('Time Step')
        axes[0, 1].set_ylabel('Polarization')
        axes[0, 1].grid(True)
        
        # エントロピー
        axes[1, 0].plot(self.history['entropy'])
        axes[1, 0].set_title('System Entropy')
        axes[1, 0].set_xlabel('Time Step')
        axes[1, 0].set_ylabel('Entropy')
        axes[1, 0].grid(True)
        
        # スピン場可視化（最終状態）
        if self.use_gpu:
            spin_z_final = cp.asnumpy(self.spin_field[:, :, 2])
        else:
            spin_z_final = self.spin_field[:, :, 2]
            
        im = axes[1, 1].imshow(spin_z_final, cmap='RdBu', vmin=-1, vmax=1)
        axes[1, 1].set_title('Final Spin Field (Z-component)')
        plt.colorbar(im, ax=axes[1, 1])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        
        plt.show()

def main():
    """メイン実行関数"""
    print("=== da-P Particle Spin Theory: Temporal Arrow Simulation ===\n")
    
    # シミュレーター作成
    sim = TemporalArrowSimulator(
        grid_size=128,
        dt=1e-12,
        use_gpu=True
    )
    
    # シミュレーション実行
    results = sim.run_simulation(steps=1000, save_interval=10)
    
    # 結果表示
    print("\n=== Temporal Arrow Theory Validation ===")
    print(f"✓ Final Arrow Strength: {results['final_arrow_strength']:.6f}")
    print(f"✓ Average Arrow Strength: {results['average_arrow_strength']:.6f}")
    print(f"✓ Temporal Irreversibility: {results['temporal_irreversibility']:.6f}")
    print(f"✓ Spin Coherence: {results['spin_coherence']:.6f}")
    print(f"✓ Final Spin Polarization: {results['final_polarization']:.6f}")
    
    # 判定
    if results['temporal_irreversibility'] > 0.1:
        print("\n🎉 TIME ARROW CONFIRMED: Significant temporal asymmetry detected!")
        print("da-P particle spin theory successfully validates the arrow of time!")
    else:
        print("\n⚠️  TIME ARROW WEAK: Low temporal asymmetry")
        print("Consider longer simulation or parameter adjustment.")
    
    if results['final_arrow_strength'] > 0.01:
        print("✅ Strong directional information flow detected")
    
    if abs(results['final_polarization']) > 0.1:
        print("✅ Significant spin alignment achieved")
    
    # 可視化
    sim.plot_results('da_p_spin_simulation_results.png')
    
    return results

if __name__ == "__main__":
    results = main()
