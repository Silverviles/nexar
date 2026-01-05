"""Service for creating visualizations"""
import io
import base64
import matplotlib.pyplot as plt
from typing import Dict

class VisualizationService:
    @staticmethod
    def fig_to_base64(fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
    
    @staticmethod
    def create_enhanced_histogram(counts: Dict[str, int], shots: int):
        """Create histogram with all basis states displayed"""
        # Get all possible 2-qubit basis states
        all_states = ['00', '01', '10', '11']
        
        # Ensure all states are in counts dictionary
        for state in all_states:
            if state not in counts:
                counts[state] = 0
        
        # Sort by state
        sorted_counts = dict(sorted(counts.items()))
        
        # Create figure with better layout
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot bars
        states = list(sorted_counts.keys())
        values = list(sorted_counts.values())
        
        bars = ax.bar(states, values, color='skyblue', edgecolor='black')
        
        # Add value labels on top of bars
        for bar, value in zip(bars, values):
            if value > 0:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height + max(values) * 0.01,
                    f'{value}\n({value/shots:.1%})',
                    ha='center',
                    va='bottom',
                    fontsize=9
                )
        
        # Set labels and title
        ax.set_xlabel('Measurement Outcome', fontsize=12)
        ax.set_ylabel('Counts', fontsize=12)
        ax.set_title(f'Quantum Measurement Results (Shots: {shots})', fontsize=14, fontweight='bold')
        
        # Set y-axis limit with some padding
        ax.set_ylim(0, max(values) * 1.15)
        
        # Add grid for better readability
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        return fig

# Singleton instance
visualization_service = VisualizationService()