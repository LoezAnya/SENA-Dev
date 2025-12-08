package com.api.nequiclone.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.api.nequiclone.dto.request.LoginRequestDTO;
import com.api.nequiclone.dto.request.RegistrationRequestDTO;
import com.api.nequiclone.entity.User;
import com.api.nequiclone.service.interfaces.AuthenticationService;

@RestController
@RequestMapping("/api/v1/auth")
public class AuthenticationController {
    private final AuthenticationService authService;

    public AuthenticationController(AuthenticationService authService) {
        this.authService = authService;
    }

    @PostMapping("/login")
    public ResponseEntity<String> login(@RequestBody LoginRequestDTO request) {
        String result = authService.login(request);
        if ("Autenticación satisfactoria".equals(result)) {
            return ResponseEntity.ok(result);
        } else {
            return ResponseEntity.status(401).body(result);
        }
    }

    @PostMapping("/signup")
    public ResponseEntity<?> register(@RequestBody RegistrationRequestDTO request) {
        User user = authService.register(request);
        if (user == null) {

            return ResponseEntity.badRequest().body("Error en el registro (usuario existente o datos inválidos)");
        }
        return ResponseEntity.ok(user);
    }
}
