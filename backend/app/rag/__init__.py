# CivicSense AI — RAG Package
# Owner: Arpit (Person 1)
#
# Keep package imports lightweight. Production RAG dependencies (NumPy,
# sentence-transformers, and Qdrant) are imported by their implementation
# modules, not merely by importing the mock provider or API application.
