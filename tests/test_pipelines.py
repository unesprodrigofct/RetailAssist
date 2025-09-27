"""Tests for the pipelines module."""

import pytest
import numpy as np
import pandas as pd

from retail_assist.core.pipelines.text import TextClusteringPipeline, create_sample_documents
from retail_assist.core.pipelines.regression import RegressionPipeline, create_sample_regression_data


class TestTextClusteringPipeline:
    """Test text clustering pipeline."""
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        pipeline = TextClusteringPipeline(n_clusters=3, max_features=100)
        assert pipeline.pipeline_name == "text_clustering"
        assert "clustering" in pipeline.models
    
    def test_preprocess(self):
        """Test text preprocessing."""
        pipeline = TextClusteringPipeline(min_doc_length=5)
        
        documents = [
            "This is a long document with enough content",
            "Short",  # Should be filtered out
            "Another good document for testing purposes",
            "",  # Should be filtered out
            "Final document with sufficient length"
        ]
        
        processed = pipeline.preprocess(documents)
        assert len(processed) == 3  # Only 3 documents should pass the filter
    
    def test_train_pipeline(self):
        """Test pipeline training."""
        pipeline = TextClusteringPipeline(n_clusters=2, max_features=50)
        documents = create_sample_documents()
        
        # Train pipeline
        pipeline.train_pipeline(documents)
        
        # Check if model is trained
        model = pipeline.get_model("clustering")
        assert model.is_trained
        assert model.metadata["n_documents"] > 0
        assert model.metadata["n_clusters"] == 2
    
    def test_predict(self):
        """Test pipeline prediction."""
        pipeline = TextClusteringPipeline(n_clusters=2, max_features=50)
        documents = create_sample_documents()
        
        # Train pipeline
        pipeline.train_pipeline(documents)
        
        # Make predictions
        test_docs = documents[:5]
        results = pipeline.predict(test_docs)
        
        assert "clusters" in results
        assert "cluster_distribution" in results
        assert "n_clusters_found" in results
        assert len(results["clusters"]) == len(test_docs)
    
    def test_empty_documents(self):
        """Test handling of empty documents."""
        pipeline = TextClusteringPipeline()
        
        results = pipeline.predict([])
        assert "error" in results
        assert results["clusters"] == []
    
    def test_cluster_centers(self):
        """Test cluster centers extraction."""
        pipeline = TextClusteringPipeline(n_clusters=2, max_features=50)
        documents = create_sample_documents()
        
        # Train pipeline
        pipeline.train_pipeline(documents)
        
        # Get predictions with cluster centers
        results = pipeline.predict(documents[:5])
        
        if "cluster_centers" in results:
            assert isinstance(results["cluster_centers"], dict)
            assert len(results["cluster_centers"]) <= 2


class TestRegressionPipeline:
    """Test regression pipeline."""
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        pipeline = RegressionPipeline(algorithm="linear")
        assert pipeline.pipeline_name == "regression"
        assert "regressor" in pipeline.models
    
    def test_preprocess(self):
        """Test data preprocessing."""
        pipeline = RegressionPipeline()
        
        # Create test data with missing values
        data = pd.DataFrame({
            "feature_1": [1, 2, np.nan, 4, 5],
            "feature_2": [10, 20, 30, np.nan, 50],
            "category": ["A", "B", "A", "C", "B"]
        })
        
        processed = pipeline.preprocess(data)
        
        # Check that missing values are handled
        assert not np.isnan(processed).any()
        assert processed.shape[0] == 5
        assert processed.shape[1] == 3  # All columns should be numeric
    
    def test_train_pipeline_linear(self):
        """Test linear regression pipeline training."""
        pipeline = RegressionPipeline(algorithm="linear")
        X, y = create_sample_regression_data(n_samples=100)
        
        # Train pipeline
        pipeline.train_pipeline(X, y)
        
        # Check if model is trained
        model = pipeline.get_model("regressor")
        assert model.is_trained
        assert model.metadata["n_samples"] == 100
        assert model.metadata["n_features"] == 4
        assert "validation_r2" in model.metadata
    
    def test_train_pipeline_random_forest(self):
        """Test random forest regression pipeline training."""
        pipeline = RegressionPipeline(algorithm="random_forest")
        X, y = create_sample_regression_data(n_samples=100)
        
        # Train pipeline
        pipeline.train_pipeline(X, y)
        
        # Check if model is trained
        model = pipeline.get_model("regressor")
        assert model.is_trained
        assert model.metadata["algorithm"] == "random_forest"
    
    def test_predict(self):
        """Test pipeline prediction."""
        pipeline = RegressionPipeline(algorithm="linear")
        X, y = create_sample_regression_data(n_samples=100)
        
        # Train pipeline
        pipeline.train_pipeline(X, y)
        
        # Make predictions
        X_test = X.head(10)
        results = pipeline.predict(X_test)
        
        assert "predictions" in results
        assert "mean_prediction" in results
        assert "std_prediction" in results
        assert len(results["predictions"]) == 10
    
    def test_feature_importance(self):
        """Test feature importance extraction."""
        pipeline = RegressionPipeline(algorithm="random_forest")
        X, y = create_sample_regression_data(n_samples=100)
        
        # Train pipeline
        pipeline.train_pipeline(X, y)
        
        # Make predictions (should include feature importance)
        results = pipeline.predict(X.head(5))
        
        if "feature_importance" in results:
            assert isinstance(results["feature_importance"], list)
            assert len(results["feature_importance"]) == X.shape[1]
    
    def test_postprocess(self):
        """Test prediction postprocessing."""
        pipeline = RegressionPipeline()
        
        predictions = np.array([1.5, 2.3, 0.8, 3.1, 2.7])
        results = pipeline.postprocess(predictions)
        
        assert "predictions" in results
        assert "mean_prediction" in results
        assert "std_prediction" in results
        assert "min_prediction" in results
        assert "max_prediction" in results
        
        assert results["mean_prediction"] == pytest.approx(np.mean(predictions))
        assert results["min_prediction"] == pytest.approx(np.min(predictions))
        assert results["max_prediction"] == pytest.approx(np.max(predictions))


class TestPipelineIntegration:
    """Test pipeline integration and edge cases."""
    
    def test_sample_data_generation(self):
        """Test sample data generation functions."""
        # Test text documents
        documents = create_sample_documents()
        assert len(documents) > 0
        assert all(isinstance(doc, str) for doc in documents)
        assert all(len(doc) > 0 for doc in documents)
        
        # Test regression data
        X, y = create_sample_regression_data(n_samples=50)
        assert X.shape[0] == 50
        assert len(y) == 50
        assert X.shape[1] == 4  # 4 features
        assert isinstance(X, pd.DataFrame)
        assert isinstance(y, pd.Series)
    
    def test_pipeline_error_handling(self):
        """Test pipeline error handling."""
        # Test text pipeline with invalid data
        text_pipeline = TextClusteringPipeline()
        
        # Should handle empty list gracefully
        results = text_pipeline.predict([])
        assert "error" in results
        
        # Test regression pipeline with invalid data
        reg_pipeline = RegressionPipeline()
        
        # Should handle empty DataFrame gracefully
        empty_df = pd.DataFrame()
        try:
            processed = reg_pipeline.preprocess(empty_df)
            assert processed.shape[0] == 0
        except Exception:
            # It's okay if it raises an exception for empty data
            pass
    
    def test_pipeline_reproducibility(self):
        """Test that pipelines produce reproducible results."""
        # Test text clustering reproducibility
        documents = create_sample_documents()
        
        pipeline1 = TextClusteringPipeline(n_clusters=2, max_features=50)
        pipeline1.train_pipeline(documents)
        results1 = pipeline1.predict(documents[:3])
        
        pipeline2 = TextClusteringPipeline(n_clusters=2, max_features=50)
        pipeline2.train_pipeline(documents)
        results2 = pipeline2.predict(documents[:3])
        
        # Results should be similar (though not necessarily identical due to randomness)
        assert len(results1["clusters"]) == len(results2["clusters"])
        
        # Test regression reproducibility
        X, y = create_sample_regression_data(n_samples=50)
        
        pipeline1 = RegressionPipeline(algorithm="linear")
        pipeline1.train_pipeline(X, y)
        results1 = pipeline1.predict(X.head(3))
        
        pipeline2 = RegressionPipeline(algorithm="linear")
        pipeline2.train_pipeline(X, y)
        results2 = pipeline2.predict(X.head(3))
        
        # Linear regression should be deterministic
        np.testing.assert_array_almost_equal(
            results1["predictions"], 
            results2["predictions"], 
            decimal=5
        )
