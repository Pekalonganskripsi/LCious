"""
Auto-Evaluation API Endpoints

API endpoints for automatic evaluation system:
- Get cached evaluation results
- Trigger background evaluations
- Check evaluation status
- Download evaluation results as Excel
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.api.deps import get_db, get_current_admin
from app.models.user import User
from app.models.evaluation_results import EvaluationResults
from app.workers.evaluation_worker import evaluation_worker

router = APIRouter()


@router.get("/auto-evaluation/results")
async def get_auto_evaluation_results(
    force_refresh: bool = False,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get latest auto-evaluation results

    Returns complete evaluation results instantly from database cache.
    If force_refresh=True, triggers new evaluation in background.

    Args:
        force_refresh: If True, triggers new evaluation even if results exist

    Returns:
        Latest evaluation results with all metrics
    """
    try:
        # Get latest completed evaluation
        latest_eval = db.query(EvaluationResults).filter(
            EvaluationResults.is_complete == True
        ).order_by(EvaluationResults.created_at.desc()).first()

        # If no results or force refresh, trigger background evaluation
        if not latest_eval or force_refresh:
            # Trigger evaluation in background
            import threading
            thread = threading.Thread(
                target=evaluation_worker.run_evaluation,
                kwargs={"trigger": "admin_visit"}
            )
            thread.daemon = True
            thread.start()

            # If we have some results, return them (even if stale)
            if latest_eval:
                return {
                    "status": "refreshing",
                    "message": "New evaluation running in background",
                    "current_results": latest_eval.to_dict(),
                    "is_refreshing": True
                }
            else:
                return {
                    "status": "initializing",
                    "message": "First evaluation running in background",
                    "current_results": None,
                    "is_refreshing": True
                }

        # Return cached results
        return {
            "status": "success",
            "message": "Latest evaluation results",
            "results": latest_eval.to_dict(),
            "is_refreshing": False
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get evaluation results: {str(e)}"
        )


@router.get("/auto-evaluation/status")
async def get_evaluation_status(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get current evaluation system status

    Returns information about:
    - Latest evaluation status
    - When last evaluation ran
    - Whether evaluation is currently running
    - System health
    """
    try:
        # Get latest evaluation (running or completed)
        latest_eval = db.query(EvaluationResults).order_by(
            EvaluationResults.created_at.desc()
        ).first()

        running_eval = db.query(EvaluationResults).filter(
            EvaluationResults.evaluation_status == "running"
        ).first()

        return {
            "system_status": "healthy",
            "latest_evaluation": latest_eval.to_dict() if latest_eval else None,
            "currently_running": running_eval.to_dict() if running_eval else None,
            "last_evaluation_time": evaluation_worker.last_evaluation_time.isoformat() if evaluation_worker.last_evaluation_time else None,
            "can_run_evaluation": evaluation_worker.should_run_evaluation(db) if running_eval else False
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get evaluation status: {str(e)}"
        )


@router.post("/auto-evaluation/trigger")
async def trigger_evaluation(
    trigger_type: str = "manual",
    background_tasks: BackgroundTasks = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Manually trigger evaluation

    Args:
        trigger_type: Type of trigger ("manual", "test", "urgent")
        background_tasks: FastAPI BackgroundTasks

    Returns:
        Evaluation trigger confirmation
    """
    try:
        # Check if evaluation can run
        if not evaluation_worker.should_run_evaluation(db):
            running = db.query(EvaluationResults).filter(
                EvaluationResults.evaluation_status == "running"
            ).first()
            if running:
                return {
                    "status": "already_running",
                    "message": "Evaluation already in progress",
                    "evaluation_id": running.id
                }
            else:
                return {
                    "status": "too_soon",
                    "message": "Minimum interval not reached since last evaluation",
                    "last_evaluation": evaluation_worker.last_evaluation_time.isoformat() if evaluation_worker.last_evaluation_time else None
                }

        # Trigger evaluation in background
        def run_eval():
            result = evaluation_worker.run_evaluation(trigger=trigger_type)
            print(f"Background evaluation completed: {result}")

        if background_tasks:
            background_tasks.add_task(run_eval)
        else:
            import threading
            thread = threading.Thread(target=run_eval)
            thread.daemon = True
            thread.start()

        return {
            "status": "triggered",
            "message": f"Evaluation triggered by {trigger_type}",
            "trigger_type": trigger_type
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger evaluation: {str(e)}"
        )


@router.get("/auto-evaluation/download-excel")
async def download_evaluation_excel(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Download evaluation results as Excel file

    Returns complete evaluation results in Excel format with multiple sheets:
    - Cross-validation results
    - Alpha optimization
    - Algorithm comparison
    - Statistical tests
    - Per-user analysis
    - Temporal trends
    """
    try:
        # Get latest completed evaluation
        latest_eval = db.query(EvaluationResults).filter(
            EvaluationResults.is_complete == True
        ).order_by(EvaluationResults.created_at.desc()).first()

        if not latest_eval or not latest_eval.export_data:
            raise HTTPException(
                status_code=404,
                detail="No completed evaluation found with export data"
            )

        # Create Excel file
        import io
        import xlsxwriter
        from datetime import datetime

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # Add formats
        header_format = workbook.add_format({'bold': True, 'bg_color': '#4472C4', 'font_color': 'white'})
        number_format = workbook.add_format({'num_format': '0.0000'})

        # 1. Cross-Validation Results Sheet
        if latest_eval.cv_results:
            cv_sheet = workbook.add_worksheet('Cross-Validation')
            cv_sheet.write_row(0, 0, ['Alpha', 'MAE', 'RMSE', 'Hit Rate'], header_format)

            row = 1
            for alpha_key, results in latest_eval.cv_results.items():
                alpha_value = alpha_key.split('_')[1]
                cv_sheet.write_row(row, 0, [
                    alpha_value,
                    results['avg_mae'],
                    results['avg_rmse'],
                    results['avg_hit_rate']
                ])
                row += 1

        # 2. Alpha Optimization Sheet
        if latest_eval.alpha_optimization_chart:
            alpha_sheet = workbook.add_worksheet('Alpha Optimization')
            alpha_sheet.write_row(0, 0, ['Alpha', 'MAE', 'RMSE', 'Hit Rate'], header_format)

            row = 1
            for data in latest_eval.alpha_optimization_chart:
                alpha_sheet.write_row(row, 0, [
                    data['alpha'],
                    data['mae'],
                    data['rmse'],
                    data['hit_rate']
                ])
                row += 1

        # 3. Best Alpha Summary
        if latest_eval.best_alpha:
            best_sheet = workbook.add_worksheet('Best Alpha')
            best_sheet.write_row(0, 0, ['Metric', 'Value'], header_format)
            best_sheet.write_row(1, 0, ['Alpha Value', latest_eval.best_alpha['value']])
            best_sheet.write_row(2, 0, ['MAE', latest_eval.best_alpha['mae']])
            best_sheet.write_row(3, 0, ['RMSE', latest_eval.best_alpha['rmse']])
            best_sheet.write_row(4, 0, ['Hit Rate', latest_eval.best_alpha['hit_rate']])

        # 4. Data Sparsity Analysis
        if latest_eval.data_sparsity and 'error' not in latest_eval.data_sparsity:
            sparsity_sheet = workbook.add_worksheet('Data Sparsity')
            sparsity_sheet.write_row(0, 0, ['Metric', 'Value'], header_format)
            sparsity_sheet.write_row(1, 0, ['Total Users', latest_eval.data_sparsity.get('total_users', 'N/A')])
            sparsity_sheet.write_row(2, 0, ['Total Menus', latest_eval.data_sparsity.get('total_menus', 'N/A')])
            sparsity_sheet.write_row(3, 0, ['Total Ratings', latest_eval.data_sparsity.get('total_ratings', 'N/A')])
            sparsity_sheet.write_row(4, 0, ['Possible Ratings', latest_eval.data_sparsity.get('possible_ratings', 'N/A')])
            sparsity_sheet.write_row(5, 0, ['Sparsity %', f"{latest_eval.data_sparsity.get('sparsity_percentage', 0):.2f}%"])
            sparsity_sheet.write_row(6, 0, ['Density %', f"{latest_eval.data_sparsity.get('density_percentage', 0):.2f}%"])
            sparsity_sheet.write_row(7, 0, ['Sparsity Level', latest_eval.data_sparsity.get('sparsity_level', 'N/A')])

        # 5. Statistical Tests
        if latest_eval.statistical_test and 'error' not in latest_eval.statistical_test:
            stats_sheet = workbook.add_worksheet('Statistical Tests')
            stats_sheet.write_row(0, 0, ['Metric', 'Value'], header_format)
            stats_sheet.write_row(1, 0, ['Alpha 1', latest_eval.statistical_test.get('alpha1', 'N/A')])
            stats_sheet.write_row(2, 0, ['Alpha 2', latest_eval.statistical_test.get('alpha2', 'N/A')])
            stats_sheet.write_row(3, 0, ['Mean Error Alpha 1', f"{latest_eval.statistical_test.get('mean_error_alpha1', 0):.4f}"])
            stats_sheet.write_row(4, 0, ['Mean Error Alpha 2', f"{latest_eval.statistical_test.get('mean_error_alpha2', 0):.4f}"])
            stats_sheet.write_row(5, 0, ['Mean Difference', f"{latest_eval.statistical_test.get('mean_difference', 0):.4f}"])
            stats_sheet.write_row(6, 0, ['T-Statistic', f"{latest_eval.statistical_test.get('t_statistic', 0):.4f}"])
            stats_sheet.write_row(7, 0, ['P-Value', f"{latest_eval.statistical_test.get('p_value', 0):.4f}"])
            stats_sheet.write_row(8, 0, ['Is Significant', 'Yes' if latest_eval.statistical_test.get('is_significant', False) else 'No'])
            stats_sheet.write_row(9, 0, ['Effect Size', f"{latest_eval.statistical_test.get('effect_size', 0):.4f}"])
            stats_sheet.write_row(10, 0, ['Effect Interpretation', latest_eval.statistical_test.get('effect_interpretation', 'N/A')])
            stats_sheet.write_row(11, 0, ['95% CI Lower', f"{latest_eval.statistical_test.get('ci_95_lower', 0):.4f}"])
            stats_sheet.write_row(12, 0, ['95% CI Upper', f"{latest_eval.statistical_test.get('ci_95_upper', 0):.4f}"])

        # 6. Per-User Analysis
        if latest_eval.per_user_analysis and 'error' not in latest_eval.per_user_analysis:
            per_user_sheet = workbook.add_worksheet('Per-User Analysis')

            # User Segments
            if latest_eval.per_user_analysis.get('user_segments'):
                row = 0
                per_user_sheet.write(row, 0, 'User Segment Analysis', header_format)
                row += 1
                per_user_sheet.write_row(row, 0, ['Segment', 'Count', 'Avg MAE', 'Std MAE', 'Min Error', 'Max Error'], header_format)
                row += 1

                for segment_name, segment_data in latest_eval.per_user_analysis['user_segments'].items():
                    per_user_sheet.write_row(row, 0, [
                        segment_name,
                        segment_data.get('count', 0),
                        f"{segment_data.get('avg_mae', 0):.4f}",
                        f"{segment_data.get('std_mae', 0):.4f}",
                        f"{segment_data.get('min_error', 0):.4f}",
                        f"{segment_data.get('max_error', 0):.4f}"
                    ])
                    row += 1

                row += 1

            # Best Predictions
            if latest_eval.per_user_analysis.get('best_predictions'):
                per_user_sheet.write(row, 0, 'Best Predictions (Lowest Error)', header_format)
                row += 1
                per_user_sheet.write_row(row, 0, ['Customer Name', 'Menu Name', 'Actual', 'Predicted', 'Error'], header_format)
                row += 1

                for pred in latest_eval.per_user_analysis['best_predictions'][:10]:
                    per_user_sheet.write_row(row, 0, [
                        pred.get('customer_name', 'Unknown'),
                        pred.get('menu_name', 'Unknown'),
                        pred.get('actual_rating', 0),
                        pred.get('predicted_rating', 0),
                        f"{pred.get('error', 0):.4f}"
                    ])
                    row += 1

                row += 1

            # Worst Predictions
            if latest_eval.per_user_analysis.get('worst_predictions'):
                per_user_sheet.write(row, 0, 'Worst Predictions (Highest Error)', header_format)
                row += 1
                per_user_sheet.write_row(row, 0, ['Customer Name', 'Menu Name', 'Actual', 'Predicted', 'Error'], header_format)
                row += 1

                for pred in latest_eval.per_user_analysis['worst_predictions'][:10]:
                    per_user_sheet.write_row(row, 0, [
                        pred.get('customer_name', 'Unknown'),
                        pred.get('menu_name', 'Unknown'),
                        pred.get('actual_rating', 0),
                        pred.get('predicted_rating', 0),
                        f"{pred.get('error', 0):.4f}"
                    ])
                    row += 1

        # 7. Algorithm Comparison
        if latest_eval.algorithm_comparison and 'error' not in latest_eval.algorithm_comparison:
            comp_sheet = workbook.add_worksheet('Algorithm Comparison')
            comp_sheet.write_row(0, 0, ['Algorithm', 'Alpha', 'MAE', 'RMSE', 'Hit Rate', 'Predictions'], header_format)

            row = 1
            for alg_name, alg_data in latest_eval.algorithm_comparison.items():
                if alg_name not in ['winner', 'winner_mae', 'total_ratings', 'test_size']:
                    comp_sheet.write_row(row, 0, [
                        alg_name,
                        alg_data.get('alpha', 'N/A'),
                        f"{alg_data.get('mae', 0):.4f}",
                        f"{alg_data.get('rmse', 0):.4f}",
                        f"{alg_data.get('hit_rate', 0):.4f}",
                        alg_data.get('predictions', 0)
                    ])
                    row += 1

            if 'winner' in latest_eval.algorithm_comparison:
                comp_sheet.write(row + 1, 0, 'Winner')
                comp_sheet.write(row + 1, 1, latest_eval.algorithm_comparison['winner'])
                comp_sheet.write(row + 2, 1, f"Winner MAE: {latest_eval.algorithm_comparison.get('winner_mae', 0):.4f}")

        # 8. Baseline Comparison
        if latest_eval.baseline_comparison and 'error' not in latest_eval.baseline_comparison:
            baseline_sheet = workbook.add_worksheet('Baseline Comparison')
            baseline_sheet.write_row(0, 0, ['Algorithm', 'MAE', 'RMSE', 'Predictions'], header_format)

            row = 1
            for alg_name, alg_data in latest_eval.baseline_comparison.items():
                if alg_name not in ['winner', 'winner_mae', 'total_ratings', 'test_size']:
                    baseline_sheet.write_row(row, 0, [
                        alg_name,
                        f"{alg_data.get('mae', 0):.4f}",
                        f"{alg_data.get('rmse', 0):.4f}",
                        alg_data.get('predictions', 0)
                    ])
                    row += 1

            if 'winner' in latest_eval.baseline_comparison:
                baseline_sheet.write(row + 1, 0, 'Winner')
                baseline_sheet.write(row + 1, 1, latest_eval.baseline_comparison['winner'])
                baseline_sheet.write(row + 2, 1, f"Winner MAE: {latest_eval.baseline_comparison.get('winner_mae', 0):.4f}")

        # 9. Temporal Analysis
        if latest_eval.temporal_analysis and 'error' not in latest_eval.temporal_analysis:
            temporal_sheet = workbook.add_worksheet('Temporal Analysis')

            row = 0
            temporal_sheet.write_row(row, 0, ['Date', 'Total Ratings', 'Cumulative', 'Avg Rating', 'Std Rating'], header_format)
            row += 1

            for day_data in latest_eval.temporal_analysis.get('daily_metrics', []):
                temporal_sheet.write_row(row, 0, [
                    day_data.get('date', 'N/A'),
                    day_data.get('total_ratings', 0),
                    day_data.get('cumulative_ratings', 0),
                    f"{day_data.get('avg_rating', 0):.2f}",
                    f"{day_data.get('std_rating', 0):.2f}"
                ])
                row += 1

            # Trend info
            row += 1
            temporal_sheet.write(row, 0, 'Trend Analysis')
            row += 1
            temporal_sheet.write_row(row, 0, ['Days Analyzed', latest_eval.temporal_analysis.get('days_analyzed', 'N/A')])
            row += 1
            temporal_sheet.write_row(row, 0, ['Trend', latest_eval.temporal_analysis.get('trend', 'N/A')])
            row += 1
            temporal_sheet.write_row(row, 0, ['Improvement %', f"{latest_eval.temporal_analysis.get('improvement_percentage', 0):.2f}%"])
            row += 1
            temporal_sheet.write_row(row, 0, ['First Period Avg', f"{latest_eval.temporal_analysis.get('first_period_avg', 0):.2f}"])
            row += 1
            temporal_sheet.write_row(row, 0, ['Second Period Avg', f"{latest_eval.temporal_analysis.get('second_period_avg', 0):.2f}"])

        # 10. Export Metadata
        meta_sheet = workbook.add_worksheet('Metadata')
        meta_sheet.write_row(0, 0, ['Field', 'Value'], header_format)
        meta_sheet.write_row(1, 0, ['Evaluation ID', latest_eval.id])
        meta_sheet.write_row(2, 0, ['Created At', latest_eval.created_at.strftime('%Y-%m-%d %H:%M:%S')])
        meta_sheet.write_row(3, 0, ['Total Ratings', latest_eval.total_ratings])
        meta_sheet.write_row(4, 0, ['Total Customers', latest_eval.total_customers])
        meta_sheet.write_row(5, 0, ['Total Menus', latest_eval.total_menus])
        meta_sheet.write_row(6, 0, ['Duration (seconds)', f"{latest_eval.evaluation_duration_seconds:.2f}"])

        # Research metadata
        if latest_eval.export_data:
            row = 7
            meta_sheet.write_row(row, 0, ['Research Information'])
            row += 1
            meta_sheet.write_row(row, 0, ['Trigger', latest_eval.export_data.get('trigger', 'N/A')])
            row += 1
            meta_sheet.write_row(row, 0, ['Timestamp', latest_eval.export_data.get('timestamp', 'N/A')])

            if latest_eval.data_sparsity and 'error' not in latest_eval.data_sparsity:
                row += 1
                meta_sheet.write_row(row, 0, ['Dataset Characteristics'])
                row += 1
                meta_sheet.write_row(row, 0, ['Sparsity Level', latest_eval.data_sparsity.get('sparsity_level', 'N/A')])
                row += 1
                meta_sheet.write_row(row, 0, ['Cold Start Problem', 'Severe' if latest_eval.data_sparsity.get('sparsity_percentage', 0) > 80 else 'Moderate'])

        workbook.close()

        # Prepare response
        output.seek(0)

        from fastapi.responses import Response
        filename = f"evaluation_results_{latest_eval.created_at.strftime('%Y%m%d_%H%M%S')}.xlsx"

        return Response(
            content=output.read(),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate Excel file: {str(e)}"
        )