package com.ecommerce.identity.service;

import com.ecommerce.common.exception.UnauthorizedException;
import com.ecommerce.identity.dto.TokenResponse;
import com.ecommerce.identity.entity.AdminUser;
import com.ecommerce.identity.repository.AdminUserRepository;
import com.ecommerce.identity.security.JwtService;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AdminAuthService {

    private final AdminUserRepository adminUserRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AdminAuthService(AdminUserRepository adminUserRepository, PasswordEncoder passwordEncoder, JwtService jwtService) {
        this.adminUserRepository = adminUserRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    public TokenResponse login(String username, String rawPassword) {
        AdminUser admin = adminUserRepository.findByUsername(username)
                .orElseThrow(() -> new UnauthorizedException("Invalid credentials"));
        if (!passwordEncoder.matches(rawPassword, admin.getPasswordHash())) {
            throw new UnauthorizedException("Invalid credentials");
        }
        String access = jwtService.generateAccessToken(admin.getUsername(), admin.getRole());
        String refresh = jwtService.generateRefreshToken(admin.getUsername(), admin.getRole());
        return new TokenResponse(access, refresh, admin.getRole());
    }
}
