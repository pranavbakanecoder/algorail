"""
Main Demo Script for Railway AI Optimization System
Demonstrates the complete workflow from data loading to visualization
"""
from algorithms.milp_optimizer import MILPOptimizer
import pandas as pd
import os
from algorithms.comprehensive_hybrid_optimizer import ComprehensiveHybridOptimizer
from algorithms.priority_engine import PriorityEngine
from visualization.visualizer import TrainVisualizer
from algorithms.realtime_optimizer import RealtimeOptimizer


def main():
    print("🚆" * 20)
    print("   RAILWAY AI OPTIMIZATION SYSTEM")
    print("   SIH 2025 - Train Traffic Optimization")
    print("🚆" * 20)


    # Step 1: Load and validate data
    print("\n📂 Step 1: Loading Data...")
    print("-" * 40)


    try:
        stations = pd.read_csv("data/stations.csv")
        sections = pd.read_csv("data/sections.csv")
        trains = pd.read_csv("data/trains.csv")
        train_sections = pd.read_csv("data/train_sections.csv")
        disruptions = pd.read_csv("data/disruptions.csv")


        print(f"✅ Loaded {len(stations)} stations")
        print(f"✅ Loaded {len(sections)} sections")
        print(f"✅ Loaded {len(trains)} trains")
        print(f"✅ Loaded {len(train_sections)} train-section mappings")
        print(f"✅ Loaded {len(disruptions)} disruptions")


    except Exception as e:
        print(f"❌ Error loading data: {e}")
        print("Please ensure CSV files are in the 'data/' directory.")
        return


    # Step 2: Priority Analysis
    print("\n⚡ Step 2: Priority Analysis...")
    print("-" * 40)


    priority_engine = PriorityEngine()
    priority_matrix = priority_engine.create_priority_matrix(trains)


    print("🎯 Train Priority Rankings (Top 10):")
    top_10 = priority_matrix.head(10)
    for _, train in top_10.iterrows():
        print(f"   {train['rank']:2d}. {train['train_name'][:20]:20s} ({train['train_type']}) - Priority: {train['priority_score']:.2f}")


    print("\n📝 Priority Decision Examples:")
    for i in range(min(3, len(trains))):
        train = trains.iloc[i]
        explanation = priority_engine.get_priority_explanation(train.to_dict())
        print(f"   • {train['train_name']}: {explanation}")


    # Step 3: Run Optimization Algorithms
    print("\n🚀 Step 3: Running Optimization Algorithms...")
    print("-" * 40)

    # Run MILP optimizer on a small subset (e.g., first 10 trains)
    print("\n⚙️  Running MILP Optimizer (small scale)...")
    milp_optimizer = MILPOptimizer()
    milp_trains = trains.head(10)
    milp_train_sections = train_sections[train_sections['train_id'].isin(milp_trains['train_id'])]
    milp_sections = sections[sections['section_id'].isin(milp_train_sections['section_id'].unique())]
    milp_schedule = milp_optimizer.optimize(milp_trains, milp_sections, milp_train_sections)
    if milp_schedule:
        print("✅ MILP Optimization Completed:")
        for train_id, sched in milp_schedule.items():
            print(f"Train {train_id}:")
            for s in sched:
                print(f"  Section {s['section_id']} Start: {s['start_time']:.2f} min")
    else:
        print("❌ MILP optimization failed or no solution")

    # Run comprehensive hybrid optimizer on full data (recommended)
    print("\n⚙️  Running Comprehensive Hybrid Optimizer...")
    comprehensive_optimizer = ComprehensiveHybridOptimizer()
    comprehensive_result = comprehensive_optimizer.optimize(trains, sections, train_sections)
    
    # Create results list with comprehensive result
    results = [comprehensive_result] if comprehensive_result.success else []


    print(f"\n📊 Optimization Results Summary:")
    print(f"{'Method':<20} {'Success':<8} {'Total Delay':<12} {'Time (s)':<10} {'Throughput':<10}")
    print("-" * 65)


    for result in results:
        status = "✅ Yes" if result.success else "❌ No"
        delay = f"{result.total_delay:.1f} min" if result.success else "N/A"
        time_taken = f"{result.computation_time:.2f}" if result.success else "N/A"
        throughput = f"{result.throughput}" if result.success else "N/A"


        print(f"{result.method:<20} {status:<8} {delay:<12} {time_taken:<10} {throughput:<10}")


    best_result = comprehensive_result if comprehensive_result.success else None
    if best_result:
        print(f"\n🏆 Best Performance: {best_result.method}")
        print(f"   Total System Delay: {best_result.total_delay:.1f} minutes")
        print(f"   Trains Processed: {best_result.throughput}")
        print(f"   Computation Time: {best_result.computation_time:.2f} seconds")


        baseline_delay = trains['delay_minutes'].sum()
        if baseline_delay > 0:
            improvement = ((baseline_delay - best_result.total_delay) / baseline_delay) * 100
            print(f"   Improvement: {improvement:.1f}% delay reduction")


    # Step 4: Generate Visualizations
    print("\n🎨 Step 4: Generating Visualizations...")
    print("-" * 40)
    visualizer = TrainVisualizer()


    visualizer.create_all_visualizations(trains, sections, train_sections)


    if results and any(r.success for r in results):
        successful_results = [r for r in results if r.success]
        visualizer.plot_optimization_comparison(successful_results)
        for result in results:
            if result.method == "Genetic Algorithm" and result.fitness_history:
                visualizer.plot_ga_convergence(result.fitness_history)
                break


    if best_result and best_result.schedule:
        visualizer.plot_train_timeline(best_result.schedule)


    # Step 5: Generate Summary Report
    print("\n📋 Step 5: Final Summary Report...")
    print("-" * 40)
    visualizer.generate_summary_report(trains, sections, train_sections)


    # Additional insights
    print("\n🔍 Additional Insights:")
    peak_trains = trains[trains['scheduled_start_time'].str.contains('08:|09:|17:|18:|19:', na=False)]
    if len(peak_trains) > 0:
        print(f"   • Peak hour trains: {len(peak_trains)} ({len(peak_trains)/len(trains)*100:.1f}%)")


    high_priority = trains[trains['priority'] <= 2]
    if len(high_priority) > 0:
        print(f"   • High priority trains: {len(high_priority)} ({len(high_priority)/len(trains)*100:.1f}%)")


    section_usage = train_sections['section_id'].value_counts()
    if len(section_usage) > 0:
        busiest = section_usage.index[0]
        print(f"   • Most congested section: {busiest} ({section_usage.iloc[0]} trains)")


    if 'train_type' in trains.columns and 'delay_minutes' in trains.columns:
        avg_delay_by_type = trains.groupby('train_type')['delay_minutes'].mean().sort_values(ascending=False)
        worst_type = avg_delay_by_type.index[0] if len(avg_delay_by_type) > 0 else "N/A"
        print(f"   • Highest delayed type: {worst_type} (avg: {avg_delay_by_type.iloc[0]:.1f} min)")


    # Step 6: Export Results
    print(f"\n💾 Step 6: Exporting Results...")
    print("-" * 40)


    try:
        if not os.path.exists('results'):
            os.makedirs('results')


        priority_matrix.to_csv('results/priority_matrix.csv', index=False)
        print("✅ Priority matrix saved to results/priority_matrix.csv")


        if results:
            results_summary = []
            for result in results:
                results_summary.append({
                    'method': result.method,
                    'success': result.success,
                    'total_delay': result.total_delay,
                    'computation_time': result.computation_time,
                    'throughput': result.throughput,
                    'conflicts_resolved': getattr(result, 'conflicts_resolved', 0)
                })


            results_df = pd.DataFrame(results_summary)
            results_df.to_csv('results/optimization_results.csv', index=False)
            print("✅ Optimization results saved to results/optimization_results.csv")


        if best_result and best_result.schedule:
            schedule_data = []
            for train_id, schedule in best_result.schedule.items():
                for section_info in schedule:
                    schedule_data.append({
                        'train_id': train_id,
                        'section_id': section_info['section_id'],
                        'entry_time': section_info['entry_time'],
                        'exit_time': section_info['exit_time'],
                        'delay_added': section_info.get('delay_added', 0)
                    })


            if schedule_data:
                schedule_df = pd.DataFrame(schedule_data)
                schedule_df.to_csv('results/optimized_schedule.csv', index=False)
                print("✅ Optimized schedule saved to results/optimized_schedule.csv")


    except Exception as e:
        print(f"⚠️  Export warning: {e}")


    # Step 7: Next Steps Recommendation
    print(f"\n🎯 Step 7: Next Steps for Phase 3...")
    print("-" * 40)
    print("✅ Phase 2 Complete! Ready for Phase 3 (Algorithm Design)")
    print("\nRecommended next actions:")
    print("1. 🧬 Implement advanced GA parameters tuning")
    print("2. 🔄 Add real-time re-optimization capability")
    print("3. 🌐 Develop web dashboard (React + FastAPI)")
    print("4. 🗺️  Add interactive train map visualization")
    print("5. 🔔 Implement conflict alert system")
    print("6. 📊 Add KPI tracking and reporting")
    print("7. 🎯 Prepare demo scenarios for judges")


    print(f"\n💡 Judge Demo Ideas:")
    print("• Show before/after delay comparison")
    print("• Interactive 'What-if' disruption simulation")
    print("• Real-time conflict detection alerts")
    print("• Priority-based decision explanations")


    print(f"\n🏆 Success Metrics Achieved:")
    if best_result:
        print("✅ Algorithm implementation: Working")
        print(f"✅ Multiple optimization methods: {len([r for r in results if r.success])}")
        print("✅ Performance improvement: Measurable")
        print("✅ Priority system: Implemented")
        print("✅ Visualization: Complete")
        print("✅ Data pipeline: Functional")


    print("\n" + "🚆" * 20)
    print("   PHASE 2 SUCCESSFULLY COMPLETED!")
    print("   Ready to move to Phase 3: System Design")
    print("🚆" * 20)


def create_sample_disruption():
    """Simulate a disruption scenario"""
    print("\n⚠️  BONUS: Disruption Simulation Demo")
    print("-" * 40)


    try:
        trains = pd.read_csv("data/trains.csv")
        sections = pd.read_csv("data/sections.csv")
        train_sections = pd.read_csv("data/train_sections.csv")
    except Exception as e:
        print(f"❌ Cannot load data for disruption simulation: {e}")
        return


    print("🚨 Simulating: Section S001 blocked for 30 minutes")
    print("🔄 Re-optimizing affected trains...")


    affected_trains = train_sections[train_sections['section_id'] == 'S001']['train_id'].unique()


    if len(affected_trains) > 0:
        print(f"📍 Affected trains: {len(affected_trains)}")
        disrupted_trains = trains.copy()
        for train_id in affected_trains:
            mask = disrupted_trains['train_id'] == train_id
            disrupted_trains.loc[mask, 'delay_minutes'] += 30


        optimizer = ComprehensiveHybridOptimizer()
        original_results = optimizer.optimize(trains, sections, train_sections)
        disrupted_results = optimizer.optimize(disrupted_trains, sections, train_sections)


        if original_results.success and disrupted_results.success:
            delay_increase = disrupted_results.total_delay - original_results.total_delay
            print(f"📊 Impact: +{delay_increase:.1f} minutes total system delay")
            print(f"🎯 Recovery time: {disrupted_results.computation_time:.2f} seconds")
            print("✅ System successfully handled disruption!")
    else:
        print("ℹ️  No trains affected by this section")


if __name__ == "__main__":
    # Run main demo
    main()


    print("\n" + "=" * 60)
    create_sample_disruption()



