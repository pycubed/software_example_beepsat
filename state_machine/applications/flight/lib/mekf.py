# Multiplicative Extended Kalman Filter
# Based on Zac Manchester's Formulation
# Writen by Aleksei Seletskiy
try:
    from ulab.numpy import dot as matmul, eye as I, zeros, array, linalg  # noqa: E741 (I is not ambiguous)
except Exception:
    from numpy import linalg, matmul, eye as I, zeros, array  # noqa: E741 (I is not ambiguous)
from lib.mathutils import Left, hat, block
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
    return matmul(Left(q), block([[array([[cos(θ / 2)]])],
                                  [r * sin(θ / 2)]]))

def step(
    ω,
    δt,
    nr_mag,
    nr_sun,
    br_mag,
    br_sun
):
    global q
    global β
    global P

    W = I(6) * 1e-6
    V = I(6) * 1e-6
    # Predict
    q_p = f(q, β, ω, δt)  # β remains constant

    # The following is equivalent to:
    # R = exp(-hat(ω-β) * δt)
    v = - (ω - β)
    mag = linalg.norm(v)
    v̂   = hat(v / mag)
    R = I(3) + (v̂) * sin(mag * δt) + matmul(v̂, v̂) * (1 - cos(mag * δt))

    A = block([
        [R,              (-δt * I(3))],
        [zeros((3, 3)),  I(3)]])
    P_p = matmul(A, matmul(P, A.tranpose())) + W

    # Innovation

    Q = Left(q_p).transpose()
    body_measurements = block([[br_mag],
                               [br_sun]])
    inertial_measurements = block([[nr_mag],
                                   [nr_sun]])
    inertial_to_body = block([[Q,            zeros(3, 3)],
                              [zeros(3, 3),  Q]])
    Z = body_measurements - matmul(inertial_to_body, inertial_measurements)
    C = block([[hat(ᵇr_mag), zeros(3, 3)],
               [hat(ᵇr_sun), zeros(3, 3)]])
    S = C * P_p * C.transpose() + V

    # Kalman Gain

    L = P_p * C.transpose() * linalg.inv(S)

    # Update

    δx = L * Z
    ϕ = δx[1:3]
    δβ = δx[4:6]
    θ = linalg.norm(ϕ)
    r = ϕ / θ
    q_u = matmul(Left(q_p), block([[array([[cos(θ / 2)]])],
                                  [r * sin(θ / 2)]]))
    β_u = β + δβ
    e1 = (I(6) - matmul(L, C))                # I(6) - LC
    e2 = (I(6) - matmul(L, C)).transpose()    # (I(6) - LC)'
    e3 = matmul(e1, matmul(P_p, e2))          # e1 * P_p * e2
    e4 = matmul(L, matmul(V, L.transpose()))  # LVL'
    P_u = e3 + e4
    # Pᵤ = (I(6) - LC) * Pₚ * (I(6) - LC)' + LVL'

    q = q_u
    β = β_u
    P = P_u
