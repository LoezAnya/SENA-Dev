package com.api.nequiclone.service.implementation;

import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.api.nequiclone.dto.request.LoginRequestDTO;
import com.api.nequiclone.dto.request.RegistrationRequestDTO;
import com.api.nequiclone.entity.Account;
import com.api.nequiclone.entity.User;
import com.api.nequiclone.repository.AccountRepository;
import com.api.nequiclone.repository.UserRepository;
import com.api.nequiclone.service.interfaces.AuthenticationService;

@Service
public class AuthenticationServiceImpl implements AuthenticationService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private AccountServiceImp accountServiceImp;

   @Autowired
    private AccountRepository accountRepository;

    public AuthenticationServiceImpl(UserRepository userRepository, PasswordEncoder passwordEncoder, AccountServiceImp accountServiceImp) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.accountServiceImp = accountServiceImp;
      
    }

    /**
     * Autenticación sencilla usando 'identification' y 'password'.
     */
    @Override
    public String login(LoginRequestDTO loginRequest) {
       
        Optional<User> optionalUser = userRepository.findByIdentification(loginRequest.getIdentification());
        if (!optionalUser.isPresent()) {
            return "Error en la autenticación"; // no detallar por seguridad
        }

        User user = optionalUser.get();
        boolean matches = passwordEncoder.matches(loginRequest.getPassword(), user.getPassword());
        if (!matches) {
            return "Error en la autenticación";
        }

        return "Autenticación satisfactoria";
    }

    /**
     * Registro sencillo usando 'identification'. Hashea la contraseña y guarda el usuario.
     */
    @Override
    @Transactional
    public User register(RegistrationRequestDTO registrationRequest) {
        // Se asume que RegistrationRequestDTO tiene getIdentification() y getPassword()
        if (registrationRequest.getIdentification() == null || registrationRequest.getPassword() == null) {
            throw new IllegalArgumentException("Faltan identification o password");
        }

        if (userRepository.findByIdentification(registrationRequest.getIdentification()).isPresent()) {
            throw new IllegalStateException("Usuario ya existe");
        }

        User newUser = new User();
        
        newUser.setIdentification(registrationRequest.getIdentification());
        newUser.setPassword(passwordEncoder.encode(registrationRequest.getPassword()));
        newUser.setEmail(registrationRequest.getEmail());
        newUser.setFirstName(registrationRequest.getFirstName());
        newUser.setLastName(registrationRequest.getLastName());
        newUser.setPhoneNumber(registrationRequest.getPhoneNumber());
        newUser.setRole(registrationRequest.getRole());       


        Account account = accountServiceImp.createAccount(newUser);
        accountRepository.save(account);

        return userRepository.save(newUser);
    }   
}
