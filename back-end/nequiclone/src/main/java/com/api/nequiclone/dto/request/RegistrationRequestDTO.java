package com.api.nequiclone.dto.request;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class RegistrationRequestDTO {
    private String identification;
    private String email;
    private String password;
    private String role;
    private String firstName;
    private String lastName;
    private String phoneNumber;
}
