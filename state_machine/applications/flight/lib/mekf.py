# Multiplicative Extended Kalman Filter
# Based on Zac Manchester's Formulation
# Writen by Aleksei Seletskiy
try:
    from ulab.numpy import block, matmul
    import ulab.linalg as linalg
except Exception:
    from numpy import linalg, block, dot as matmul
from lib.mathutils import L
from math import cos, sin

q = []  # Quaternion attitude vector
β = []  # Gyro bias vector
P = [[]]  # Covariance matrix
# mutable struct EKF
#     q::Vector{Float64}
#     β::Vector{Float64}
#     P::Matrix{Float64}
# end

def f(q, β, ω, δt):
    """State propogation function"""
    θ = linalg.norm(ω - β) * δt
    r = (ω - β) / linalg.norm(ω - β)
    return matmul(L(q), block([[cos(θ / 2)], [r * sin(θ / 2)]]))
