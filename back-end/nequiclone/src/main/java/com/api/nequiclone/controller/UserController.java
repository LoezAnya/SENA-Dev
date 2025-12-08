package com.api.nequiclone.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.api.nequiclone.dto.response.UserResponseDTO;
import com.api.nequiclone.entity.Account;
import com.api.nequiclone.entity.User;
import com.api.nequiclone.service.interfaces.AccountService;
import com.api.nequiclone.service.interfaces.UserService;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/v1/users")
public class UserController {

    @Autowired
    private UserService userService;

    @Autowired
    private AccountService accountService;

    /**
     * Endpoint para registrar un nuevo usuario.
     * Crea el usuario y automáticamente crea su cuenta asociada.
     * POST /api/v1/users/register
     */
    @PostMapping("/register")
    public ResponseEntity<?> singUp(@Valid @RequestBody User userAccountDTO) {
        try {
            // Crear el usuario
            User createdUser = userService.createUser(userAccountDTO);

            // Crear la cuenta asociada al usuario
            Account account = accountService.createAccount(createdUser);

            // Construir respuesta con usuario y cuenta
            UserResponseDTO response = new UserResponseDTO();
            response.setUser(createdUser);
            response.setAccount(account);
            response.setMessage("Usuario y cuenta creados exitosamente");

            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Error validación: " + e.getMessage());
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).body("Error: " + e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error interno: " + e.getMessage());
        }
    }

    /**
     * Endpoint para obtener un usuario por id con su cuenta asociada.
     * GET /api/v1/users/{userId}
     */
    @GetMapping("/{userId}")
    public ResponseEntity<?> getUserWithAccount(@PathVariable Long userId) {
        try {
            User user = userService.getUserById(userId);
            if (user == null) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Usuario no encontrado");
            }

            // Obtener la cuenta asociada (si existe relación directa en User)
            // Si no, usar un repositorio de Account con findByUserId
            Account account = accountService.getAccountByUserId(userId); // método a agregar si no existe

            UserResponseDTO response = new UserResponseDTO();
            response.setUser(user);
            response.setAccount(account);

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error interno: " + e.getMessage());
        }
    }
}
