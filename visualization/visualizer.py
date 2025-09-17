"""
Railway AI Visualization Package
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Dict

plt.rcParams['figure.figsize'] = [10, 6]
plt.rcParams['font.size'] = 10
sns.set_palette("husl")

class TrainVisualizer:
    """Main visualization class for train optimization results"""

    def __init__(self):
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']

    def plot_optimization_comparison(self, results: List, save_path: str = 'optimization_comparison.png'):
        if not results:
            print("⚠️ No results to plot")
            return

        methods = [getattr(r, 'method', f'Method_{i}') for i, r in enumerate(results)]
        delays = [r.total_delay for r in results]
        computation_times = [r.computation_time for r in results]
        throughputs = [r.throughput for r in results]

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

        bars1 = ax1.bar(methods, delays, color=self.colors[:len(methods)])
        ax1.set_title('🚂 Total Delay by Optimization Method', fontweight='bold')
        ax1.set_ylabel('Total Delay (minutes)')
        ax1.tick_params(axis='x', rotation=45)

        for bar, delay in zip(bars1, delays):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                     f'{delay:.1f}', ha='center', va='bottom')

        bars2 = ax2.bar(methods, computation_times, color=self.colors[:len(methods)])
        ax2.set_title('⏱️ Computation Time by Method', fontweight='bold')
        ax2.set_ylabel('Time (seconds)')
        ax2.tick_params(axis='x', rotation=45)

        for bar, time in zip(bars2, computation_times):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                     f'{time:.2f}s', ha='center', va='bottom')

        bars3 = ax3.bar(methods, throughputs, color=self.colors[:len(methods)])
        ax3.set_title('🚄 Throughput by Method', fontweight='bold')
        ax3.set_ylabel('Trains Processed')
        ax3.tick_params(axis='x', rotation=45)

        efficiency_scores = [t/(d+1) for t, d in zip(throughputs, delays)]
        bars4 = ax4.bar(methods, efficiency_scores, color=self.colors[:len(methods)])
        ax4.set_title('🎯 Efficiency Score', fontweight='bold')
        ax4.set_ylabel('Efficiency (Throughput/Delay)')
        ax4.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {save_path}")

        return fig

    def plot_ga_convergence(self, fitness_history: List[float], save_path: str = 'ga_convergence.png'):
        plt.figure(figsize=(12, 6))

        generations = list(range(len(fitness_history)))
        plt.plot(generations, fitness_history, color='#45B7D1', linewidth=2, marker='o', markersize=4)

        z = np.polyfit(generations, fitness_history, 1)
        p = np.poly1d(z)
        plt.plot(generations, p(generations), "--", color='red', alpha=0.7, label='Trend')

        plt.title('🧬 Genetic Algorithm Convergence', fontsize=14, fontweight='bold')
        plt.xlabel('Generation')
        plt.ylabel('Best Fitness Score')
        plt.grid(True, alpha=0.3)
        plt.legend()

        improvement = fitness_history[-1] - fitness_history[0]
        plt.text(0.7, 0.15, f'Improvement: {improvement:.3f}\nFinal Fitness: {fitness_history[-1]:.3f}',
                 transform=plt.gca().transAxes, bbox=dict(boxstyle="round", facecolor='wheat', alpha=0.8))

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {save_path}")

        return plt.gcf()

    def plot_train_timeline(self, schedule: Dict, save_path: str = 'train_timeline.png'):
        if not schedule or not isinstance(schedule, dict):
            print("⚠️ Invalid schedule data for timeline")
            return

        plt.figure(figsize=(16, 8))

        y_pos = 0
        colors = plt.cm.Set3(np.linspace(0, 1, len(schedule)))

        for i, (train_id, train_schedule) in enumerate(schedule.items()):
            if isinstance(train_schedule, list) and train_schedule:
                for j, section in enumerate(train_schedule):
                    start_time = j * 30
                    duration = 25

                    plt.barh(y_pos, duration, left=start_time, color=colors[i], alpha=0.7,
                             edgecolor='black', linewidth=0.5)

                    if j == 0:
                        plt.text(start_time + duration / 2, y_pos, train_id[:6],
                                 ha='center', va='center', fontsize=8, fontweight='bold')

            y_pos += 1

        plt.title('🚆 Train Schedule Timeline', fontsize=14, fontweight='bold')
        plt.xlabel('Time (minutes from start)')
        plt.ylabel('Trains')
        plt.grid(True, alpha=0.3, axis='x')

        train_labels = [train_id[:8] for train_id in schedule.keys()]
        plt.yticks(range(len(train_labels)), train_labels)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {save_path}")

        return plt.gcf()

    def plot_priority_distribution(self, trains_df: pd.DataFrame, save_path: str = 'priority_distribution.png'):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        if 'train_type' in trains_df.columns:
            type_counts = trains_df['train_type'].value_counts()

            ax1.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%',
                    colors=self.colors[:len(type_counts)], startangle=90)
            ax1.set_title('🚂 Train Type Distribution', fontweight='bold')

        if 'priority' in trains_df.columns:
            priority_counts = trains_df['priority'].value_counts().sort_index()

            bars = ax2.bar(priority_counts.index, priority_counts.values,
                           color=self.colors[:len(priority_counts)])
            ax2.set_title('⚡ Priority Level Distribution', fontweight='bold')
            ax2.set_xlabel('Priority Level (1=Highest)')
            ax2.set_ylabel('Number of Trains')

            for bar, count in zip(bars, priority_counts.values):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width() / 2., height,
                         f'{count}', ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {save_path}")

        return fig

    def plot_section_utilization(self, train_sections_df: pd.DataFrame, sections_df: pd.DataFrame,
                                save_path: str = 'section_utilization.png'):
        section_usage = train_sections_df['section_id'].value_counts()

        sections_with_usage = sections_df.merge(
            section_usage.to_frame('train_count'),
            left_on='section_id',
            right_index=True,
            how='left'
        ).fillna(0)

        plt.figure(figsize=(14, 8))

        utilization_data = sections_with_usage.pivot_table(
            values='train_count',
            index='from_station',
            columns='to_station',
            fill_value=0
        )

        sns.heatmap(utilization_data, annot=True, cmap='YlOrRd', fmt='g')
        plt.title('🗺️ Section Utilization Heatmap', fontsize=14, fontweight='bold')
        plt.xlabel('To Station')
        plt.ylabel('From Station')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {save_path}")

        return plt.gcf()

    def plot_delay_analysis(self, trains_df: pd.DataFrame, save_path: str = 'delay_analysis.png'):
        if 'delay_minutes' not in trains_df.columns:
            print("⚠️ No delay data found")
            return

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        ax1.hist(trains_df['delay_minutes'], bins=20, color='#FF6B6B', alpha=0.7, edgecolor='black')
        ax1.set_title('📊 Delay Distribution', fontweight='bold')
        ax1.set_xlabel('Delay (minutes)')
        ax1.set_ylabel('Number of Trains')
        ax1.grid(True, alpha=0.3)

        if 'train_type' in trains_df.columns:
            delay_by_type = trains_df.groupby('train_type')['delay_minutes'].mean()
            bars = ax2.bar(delay_by_type.index, delay_by_type.values,
                           color=self.colors[:len(delay_by_type)])
            ax2.set_title('⏰ Average Delay by Train Type', fontweight='bold')
            ax2.set_ylabel('Average Delay (minutes)')
            ax2.tick_params(axis='x', rotation=45)

            for bar, delay in zip(bars, delay_by_type.values):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width() / 2., height,
                         f'{delay:.1f}', ha='center', va='bottom')

        if 'priority' in trains_df.columns:
            delay_by_priority = trains_df.groupby('priority')['delay_minutes'].mean()
            ax3.plot(delay_by_priority.index, delay_by_priority.values,
                     marker='o', linewidth=2, markersize=8, color='#45B7D1')
            ax3.set_title('🎯 Delay vs Priority Level', fontweight='bold')
            ax3.set_xlabel('Priority Level')
            ax3.set_ylabel('Average Delay (minutes)')
            ax3.grid(True, alpha=0.3)

        on_time = (trains_df['delay_minutes'] <= 5).sum()
        delayed = (trains_df['delay_minutes'] > 5).sum()

        labels = ['On Time (≤5 min)', 'Delayed (>5 min)']
        sizes = [on_time, delayed]
        colors_pie = ['#96CEB4', '#FF6B6B']

        ax4.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=90)
        ax4.set_title('⚡ On-Time Performance', fontweight='bold')

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {save_path}")

        return fig

    def generate_summary_report(self, trains_df: pd.DataFrame, sections_df: pd.DataFrame,
                                train_sections_df: pd.DataFrame):
        print("\n" + "=" * 60)
        print("🚆 RAILWAY OPTIMIZATION - DATA SUMMARY REPORT")
        print("=" * 60)

        print(f"\n📊 BASIC STATISTICS:")
        print(f"   • Total Trains: {len(trains_df)}")
        print(f"   • Total Sections: {len(sections_df)}")
        print(f"   • Total Train-Section Assignments: {len(train_sections_df)}")

        if 'train_type' in trains_df.columns:
            print(f"\n🚂 TRAIN TYPE BREAKDOWN:")
            type_counts = trains_df['train_type'].value_counts()
            for train_type, count in type_counts.items():
                print(f"   • {train_type}: {count} trains")

        if 'priority' in trains_df.columns:
            print(f"\n⚡ PRIORITY ANALYSIS:")
            priority_counts = trains_df['priority'].value_counts().sort_index()
            for priority, count in priority_counts.items():
                print(f"   • Priority {priority}: {count} trains")

        if 'delay_minutes' in trains_df.columns:
            avg_delay = trains_df['delay_minutes'].mean()
            max_delay = trains_df['delay_minutes'].max()
            on_time_rate = (trains_df['delay_minutes'] <= 5).sum() / len(trains_df) * 100

            print(f"\n⏰ DELAY ANALYSIS:")
            print(f"   • Average Delay: {avg_delay:.2f} minutes")
            print(f"   • Maximum Delay: {max_delay:.0f} minutes")
            print(f"   • On-Time Performance: {on_time_rate:.1f}%")

        section_usage = train_sections_df['section_id'].value_counts()
        busiest_section = section_usage.index[0] if len(section_usage) > 0 else "N/A"

        print(f"\n🗺️ SECTION UTILIZATION:")
        print(f"   • Busiest Section: {busiest_section} ({section_usage.iloc[0] if len(section_usage) > 0 else 0} trains)")
        print(f"   • Average Trains per Section: {section_usage.mean():.1f}")

        print(f"\n🎯 KEY RECOMMENDATIONS:")
        if 'delay_minutes' in trains_df.columns and avg_delay > 15:
            print("   • High average delay detected - Consider optimization algorithms")
        if len(section_usage) > 0 and section_usage.iloc[0] > 10:
            print("   • Heavy section utilization - May need capacity planning")
        print("   • Ready for Phase 3: Algorithm Implementation")

        print("\n" + "=" * 60)

    def create_all_visualizations(self, trains_df: pd.DataFrame, sections_df: pd.DataFrame,
                                  train_sections_df: pd.DataFrame):
        print("\n🎨 Creating all visualizations...")

        self.plot_priority_distribution(trains_df)
        self.plot_delay_analysis(trains_df)
        self.plot_section_utilization(train_sections_df, sections_df)

        self.generate_summary_report(trains_df, sections_df, train_sections_df)

        print("\n✅ All visualizations completed!")
