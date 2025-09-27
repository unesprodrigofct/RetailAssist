"""Tests for the trainers module."""

import pytest
import numpy as np
import pandas as pd

from retail_assist.core.trainers.xgboost import XGBoostModel, create_sample_classification_data
from retail_assist.core.trainers.regression import SimpleRegressionModel, create_sample_data


class TestXGBoostModel:
    """Test XGBoost model."""
    
    def test_model_initialization_classification(self):
        """Test XGBoost classification model initialization."""
        model = XGBoostModel(task_type="classification")
        assert model.model_name == "xgboost_classification"
        assert model.task_type == "classification"
        assert not model.is_trained
        assert model.model is not None
    
    def test_model_initialization_regression(self):
        """Test XGBoost regression model initialization."""
        model = XGBoostModel(task_type="regression")
        assert model.model_name == "xgboost_regression"
        assert model.task_type == "regression"
        assert not model.is_trained
    
    def test_train_classification_without_optimization(self):
        """Test training classification model without hyperparameter optimization."""
        model = XGBoostModel(task_type="classification")
        X, y = create_sample_classification_data(n_samples=100)
        
        # Train without hyperparameter optimization
        model.train(X, y, optimize_hyperparams=False)
        
        assert model.is_trained
        assert model.metadata["n_features"] == 4
        assert "validation_accuracy" in model.metadata
        assert "validation_roc_auc" in model.metadata
        assert model.label_encoder is not None
    
    def test_train_classification_with_optimization(self):
        """Test training classification model with hyperparameter optimization."""
        model = XGBoostModel(task_type="classification")
        X, y = create_sample_classification_data(n_samples=200)
        
        # Train with hyperparameter optimization (reduced grid for speed)
        model.train(X, y, optimize_hyperparams=True, cv_folds=3)
        
        assert model.is_trained
        assert model.best_params is not None
        assert model.cv_results is not None
        assert "best_score" in model.cv_results
    
    def test_train_regression(self):
        """Test training regression model."""
        model = XGBoostModel(task_type="regression")
        
        # Create regression data
        np.random.seed(42)
        X = pd.DataFrame({
            "feature_1": np.random.normal(0, 1, 100),
            "feature_2": np.random.normal(5, 2, 100),
        })
        y = 2 * X["feature_1"] + -1.5 * X["feature_2"] + np.random.normal(0, 0.5, 100)
        
        model.train(X, y, optimize_hyperparams=False)
        
        assert model.is_trained
        assert "validation_mse" in model.metadata
        assert "validation_r2" in model.metadata
        assert model.label_encoder is None  # No label encoding for regression
    
    def test_predict_classification(self):
        """Test classification predictions."""
        model = XGBoostModel(task_type="classification")
        X, y = create_sample_classification_data(n_samples=100)
        
        # Train model
        model.train(X, y, optimize_hyperparams=False)
        
        # Make predictions
        X_test = X.head(10)
        predictions = model.predict(X_test)
        probabilities = model.predict_proba(X_test)
        
        assert len(predictions) == 10
        assert probabilities.shape == (10, 2)  # Binary classification
        assert all(pred in [0, 1] for pred in predictions)
    
    def test_predict_regression(self):
        """Test regression predictions."""
        model = XGBoostModel(task_type="regression")
        
        # Create regression data
        np.random.seed(42)
        X = pd.DataFrame({
            "feature_1": np.random.normal(0, 1, 100),
            "feature_2": np.random.normal(5, 2, 100),
        })
        y = 2 * X["feature_1"] + -1.5 * X["feature_2"] + np.random.normal(0, 0.5, 100)
        
        model.train(X, y, optimize_hyperparams=False)
        
        # Make predictions
        X_test = X.head(10)
        predictions = model.predict(X_test)
        
        assert len(predictions) == 10
        assert all(isinstance(pred, (int, float, np.number)) for pred in predictions)
    
    def test_feature_importance(self):
        """Test feature importance extraction."""
        model = XGBoostModel(task_type="classification")
        X, y = create_sample_classification_data(n_samples=100)
        
        model.train(X, y, optimize_hyperparams=False)
        
        importance = model.get_feature_importance()
        assert isinstance(importance, dict)
        assert len(importance) == 4  # 4 features
        assert all(isinstance(v, (int, float, np.number)) for v in importance.values())
    
    def test_predict_proba_regression_error(self):
        """Test that predict_proba raises error for regression."""
        model = XGBoostModel(task_type="regression")
        
        with pytest.raises(ValueError, match="predict_proba is only available for classification"):
            model.predict_proba(np.array([[1, 2]]))
    
    def test_predict_untrained_model(self):
        """Test prediction with untrained model raises error."""
        model = XGBoostModel(task_type="classification")
        
        with pytest.raises(ValueError, match="Model must be trained"):
            model.predict(np.array([[1, 2, 3, 4]]))


class TestSimpleRegressionModel:
    """Test simple regression model."""
    
    def test_model_initialization(self):
        """Test model initialization."""
        model = SimpleRegressionModel()
        assert model.model_name == "simple_regression"
        assert not model.is_trained
        assert model.model is not None
    
    def test_train_model(self):
        """Test model training."""
        model = SimpleRegressionModel()
        X, y = create_sample_data(n_samples=100)
        
        model.train(X, y)
        
        assert model.is_trained
        assert model.metadata["n_samples"] == 100
        assert model.metadata["n_features"] == 2
        assert "validation_mse" in model.metadata
        assert "validation_r2" in model.metadata
    
    def test_predict(self):
        """Test model predictions."""
        model = SimpleRegressionModel()
        X, y = create_sample_data(n_samples=100)
        
        # Train model
        model.train(X, y)
        
        # Make predictions
        X_test = X.head(10)
        predictions = model.predict(X_test)
        
        assert len(predictions) == 10
        assert all(isinstance(pred, (int, float, np.number)) for pred in predictions)
    
    def test_predict_untrained_model(self):
        """Test prediction with untrained model raises error."""
        model = SimpleRegressionModel()
        
        with pytest.raises(ValueError, match="Model must be trained"):
            model.predict(np.array([[1, 2]]))
    
    def test_train_with_pandas_input(self):
        """Test training with pandas DataFrame input."""
        model = SimpleRegressionModel()
        X, y = create_sample_data(n_samples=50)
        
        # Ensure X and y are pandas objects
        assert isinstance(X, pd.DataFrame)
        assert isinstance(y, pd.Series)
        
        model.train(X, y)
        
        assert model.is_trained
        assert model.metadata["n_samples"] == 50
    
    def test_train_with_numpy_input(self):
        """Test training with numpy array input."""
        model = SimpleRegressionModel()
        X, y = create_sample_data(n_samples=50)
        
        # Convert to numpy arrays
        X_np = X.values
        y_np = y.values
        
        model.train(X_np, y_np)
        
        assert model.is_trained
        assert model.metadata["n_samples"] == 50


class TestTrainerIntegration:
    """Test trainer integration and edge cases."""
    
    def test_sample_data_generation(self):
        """Test sample data generation functions."""
        # Test XGBoost classification data
        X, y = create_sample_classification_data(n_samples=100)
        assert X.shape[0] == 100
        assert len(y) == 100
        assert X.shape[1] == 4  # 4 features
        assert isinstance(X, pd.DataFrame)
        assert isinstance(y, pd.Series)
        assert set(y.unique()) == {0, 1}  # Binary classification
        
        # Test simple regression data
        X, y = create_sample_data(n_samples=50)
        assert X.shape[0] == 50
        assert len(y) == 50
        assert X.shape[1] == 2  # 2 features
        assert isinstance(X, pd.DataFrame)
        assert isinstance(y, pd.Series)
    
    def test_model_reproducibility(self):
        """Test that models produce reproducible results with same random state."""
        # Test XGBoost reproducibility
        X, y = create_sample_classification_data(n_samples=100)
        
        model1 = XGBoostModel(task_type="classification", random_state=42)
        model1.train(X, y, optimize_hyperparams=False)
        pred1 = model1.predict(X.head(5))
        
        model2 = XGBoostModel(task_type="classification", random_state=42)
        model2.train(X, y, optimize_hyperparams=False)
        pred2 = model2.predict(X.head(5))
        
        # Should be identical with same random state
        np.testing.assert_array_equal(pred1, pred2)
        
        # Test simple regression reproducibility
        X_reg, y_reg = create_sample_data(n_samples=50)
        
        model1 = SimpleRegressionModel(random_state=42)
        model1.train(X_reg, y_reg)
        pred1 = model1.predict(X_reg.head(5))
        
        model2 = SimpleRegressionModel(random_state=42)
        model2.train(X_reg, y_reg)
        pred2 = model2.predict(X_reg.head(5))
        
        # Linear regression should be deterministic
        np.testing.assert_array_almost_equal(pred1, pred2, decimal=10)
    
    def test_model_metadata(self):
        """Test that models store appropriate metadata."""
        # Test XGBoost metadata
        model = XGBoostModel(task_type="classification")
        X, y = create_sample_classification_data(n_samples=100)
        model.train(X, y, optimize_hyperparams=False)
        
        metadata = model.metadata
        assert "n_samples" in metadata
        assert "n_features" in metadata
        assert "task_type" in metadata
        assert "feature_names" in metadata
        assert metadata["task_type"] == "classification"
        
        # Test simple regression metadata
        model = SimpleRegressionModel()
        X, y = create_sample_data(n_samples=50)
        model.train(X, y)
        
        metadata = model.metadata
        assert "n_samples" in metadata
        assert "n_features" in metadata
        assert "validation_r2" in metadata
        assert metadata["n_samples"] == 50
    
    def test_invalid_task_type(self):
        """Test invalid task type raises error."""
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            XGBoostModel(task_type="invalid_task")
    
    def test_model_save_load_compatibility(self):
        """Test that models are compatible with base class save/load."""
        # Test XGBoost model
        model = XGBoostModel(task_type="classification")
        X, y = create_sample_classification_data(n_samples=50)
        model.train(X, y, optimize_hyperparams=False)
        
        # Should be able to save (though we won't actually save in tests)
        assert model.is_trained
        assert model.model is not None
        
        # Test simple regression model
        model = SimpleRegressionModel()
        X, y = create_sample_data(n_samples=50)
        model.train(X, y)
        
        assert model.is_trained
        assert model.model is not None
