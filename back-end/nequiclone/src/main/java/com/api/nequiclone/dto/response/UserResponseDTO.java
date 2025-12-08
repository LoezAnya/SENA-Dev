package com.api.nequiclone.dto.response;

import com.api.nequiclone.entity.Account;
import com.api.nequiclone.entity.User;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class UserResponseDTO {
    // Usuario registrado
    private User user;

    // Cuenta asociada
    private Account account;

    // Mensaje descriptivo
    private String message;
}