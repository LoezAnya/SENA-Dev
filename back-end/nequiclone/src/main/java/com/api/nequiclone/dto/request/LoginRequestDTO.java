package com.api.nequiclone.dto.request;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class LoginRequestDTO {
    private String identification;
    private String password;

    public LoginRequestDTO() {
    }

    public LoginRequestDTO(String identification, String password) {
        this.identification = identification;
        this.password = password;
    }
}
