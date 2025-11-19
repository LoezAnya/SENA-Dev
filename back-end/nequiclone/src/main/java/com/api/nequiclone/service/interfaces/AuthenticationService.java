package com.api.nequiclone.service.interfaces;

import com.api.nequiclone.dto.request.LoginRequestDTO;
import com.api.nequiclone.dto.request.RegistrationRequestDTO;
import com.api.nequiclone.entity.User;

public interface AuthenticationService {
    String login(LoginRequestDTO loginRequest);
    User register(RegistrationRequestDTO registrationRequest);
}
