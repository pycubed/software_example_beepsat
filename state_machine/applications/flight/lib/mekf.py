# Multiplicative Extended Kalman Filter
# Based on Zac Manchester's Formulation
# Writen by Aleksei Seletskiy
try:
    from ulab.numpy import matmul, identity as I, zeros, array  # noqa: E741 (I is not ambiguous)
    import ulab.linalg as linalg
except Exception:
    from numpy import linalg, dot as matmul, identity as I, zeros, array  # noqa: E741 (I is not ambiguous)
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
    return Left(q) @ block([[array([[cos(θ / 2)]])],
                            [r * sin(θ / 2)]])

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
    R = I(3) + (v̂) * sin(mag * δt) + (v̂ @ v̂) * (1 - cos(mag * δt))

    A = block([
        [R,              (-δt * I(3))],
        [zeros((3, 3)),  I(3)]])
    P_p = (A @ P @ A.tranpose()) + W

    # Innovation

    Q = Left(q_p).transpose()
    body_measurements = block([[br_mag],
                               [br_sun]])
    inertial_measurements = block([[nr_mag],
                                   [nr_sun]])
    inertial_to_body = block([[Q,            zeros(3, 3)],
                              [zeros(3, 3),  Q]])
    Z = body_measurements - inertial_to_body @ inertial_measurements
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
    qᵤ = Left(q_p) @ block([[array([[cos(θ / 2)]])],
                            [r * sin(θ / 2)]])
    βᵤ = β + δβ
    Pᵤ = (I(6) - L @ C) @ P_p @ (I(6) - L @ C).transpose() + L @ V @ L.transpose()

    q = qᵤ
    β = βᵤ
    P = Pᵤ


# function step(
#     e::EKF,
#     ω::Vector{Float64},
#     δt::Float64,
#     ⁿr_mag::Vector{Float64},
#     ⁿr_sun::Vector{Float64},
#     ᵇr_mag::Vector{Float64},
#     ᵇr_sun::Vector{Float64}
# )
#     q = e.q
#     β = e.β
#     P = e.P
#     W = I(6) * 1e-6 # related to some noise or something (ask Zac)
#     V = I(6) * 1e-6 # some other noise
#     # Predict:
#     qₚ = f(q, β, ω, δt) # β remains constant
#     R = exp(-hat(ω - β) * δt)
#     A = [
#         R (-δt*I(3))
#         zeros(3, 3) I(3)
#     ]
#     Pₚ = A * P * A' + W

#     # Innovation
#     Q = quaternionToMatrix(qₚ)'
#     Z = [ᵇr_mag; ᵇr_sun] - [Q zeros(3, 3); zeros(3, 3) Q] * [ⁿr_mag; ⁿr_sun]
#     C = [hat(ᵇr_mag) zeros(3, 3); hat(ᵇr_sun) zeros(3, 3)]
#     S = C * Pₚ * C' + V

#     # Kalman Gain
#     L = Pₚ * C' * inv(S)

#     # Update
#     δx = L * Z
#     ϕ = δx[1:3]
#     δβ = δx[4:6]
#     θ = norm(ϕ)
#     r = normalize(ϕ)
#     qᵤ = ⊙(qₚ, [cos(θ / 2); r * sin(θ / 2)])
#     βᵤ = e.β + δβ
#     Pᵤ = (I(6) - L * C) * Pₚ * (I(6) - L * C)' + L * V * L'

#     e.q = qᵤ
#     e.β = βᵤ
#     e.P = Pᵤ
#     return e
# end

# # for the "simplest MEKF"
# function simplest_step(
#     e::EKF,
#     ω::Vector{Float64},
#     δt::Float64,
#     ⁿr_mag::Vector{Float64},
#     ⁿr_sun::Vector{Float64},
#     ᵇr_mag::Vector{Float64},
#     ᵇr_sun::Vector{Float64}
# )
#     q = e.q
#     P = e.P
#     W = I(3) * 1e-6
#     V = I(6) * 1e-6
#     # Predict
#     r = normalize(ω)
#     θ = norm(ω) * δt
#     qₚ = ⊙(q, [cos(θ / 2); r * sin(θ / 2)])
#     Pₚ = P + W
#     # Innovation
#     Q = quaternionToMatrix(qₚ)'
#     Z = [ᵇr_mag; ᵇr_sun] - [Q zeros(3, 3); zeros(3, 3) Q] * [ⁿr_mag; ⁿr_sun]
#     C = [hat(Q * ⁿr_mag); hat(Q * ⁿr_sun)]
#     S = C * Pₚ * C' + V
#     # Kalman Gain
#     L = Pₚ * C' * inv(S)
#     # Update
#     ϕ = L * Z
#     θ = norm(ϕ)
#     r = normalize(ϕ)
#     e.q = ⊙(qₚ, [cos(θ / 2); r * sin(θ / 2)])
#     e.P = (I(3) - L * C) * Pₚ * (I(3) - L * C)' + L * V * L'
# end
