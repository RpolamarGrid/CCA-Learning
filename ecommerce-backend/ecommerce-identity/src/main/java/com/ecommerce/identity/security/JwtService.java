package com.ecommerce.identity.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import java.security.Key;
import java.util.Date;
import java.util.List;
import java.util.Map;
import javax.crypto.SecretKey;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

/**
 * Issues and parses stateless JWT access/refresh tokens for both admin and
 * customer principals. Stateless so the app tier can scale horizontally
 * without sticky sessions (see docs/adr/0006-scaling-to-1m-users.md).
 */
@Service
public class JwtService {

    private final Key signingKey;
    private final long accessTokenTtlMillis;
    private final long refreshTokenTtlMillis;

    public JwtService(
            @Value("${app.jwt.signing-key}") String signingKeyBase64,
            @Value("${app.jwt.access-ttl-minutes:15}") long accessTtlMinutes,
            @Value("${app.jwt.refresh-ttl-minutes:10080}") long refreshTtlMinutes) {
        this.signingKey = Keys.hmacShaKeyFor(signingKeyBase64.getBytes());
        this.accessTokenTtlMillis = accessTtlMinutes * 60_000L;
        this.refreshTokenTtlMillis = refreshTtlMinutes * 60_000L;
    }

    public String generateAccessToken(String subject, String role) {
        return buildToken(subject, role, "access", accessTokenTtlMillis);
    }

    public String generateRefreshToken(String subject, String role) {
        return buildToken(subject, role, "refresh", refreshTokenTtlMillis);
    }

    private String buildToken(String subject, String role, String tokenType, long ttlMillis) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + ttlMillis);
        return Jwts.builder()
                .subject(subject)
                .claims(Map.of("role", role, "type", tokenType))
                .issuedAt(now)
                .expiration(expiry)
                .signWith((SecretKey) signingKey)
                .compact();
    }

    public Claims parseClaims(String token) {
        return Jwts.parser()
                .verifyWith((SecretKey) signingKey)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    public List<String> rolesOf(Claims claims) {
        Object role = claims.get("role");
        return role == null ? List.of() : List.of(role.toString());
    }
}
