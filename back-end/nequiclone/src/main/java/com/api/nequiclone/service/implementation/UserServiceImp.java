package com.api.nequiclone.service.implementation;


import java.util.Objects;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.api.nequiclone.entity.Account;
import com.api.nequiclone.entity.User;

import com.api.nequiclone.repository.AccountRepository;
import com.api.nequiclone.repository.UserRepository;
import com.api.nequiclone.service.interfaces.UserService;

@Service
public class UserServiceImp implements UserService {

    @Autowired
    private UserRepository userRepository;
    
    private AccountServiceImp accountServiceImp;

    @Autowired
    private AccountRepository accountRepository;

    @Override
    public User createUser(User dto) {
        Objects.requireNonNull(dto, "User dto cannot be null");

        User user = new User(dto);
        User savedUser = userRepository.save(user);

        Account account = accountServiceImp.createAccount(savedUser);
        accountRepository.save(account);

        return savedUser;
     }

    @Override
    public User getUserById(Long id) {
        return null;
        
        
    }

    @Override
    public User getUserByEmail(String email) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'getUserByEmail'");
    }

    @Override
    public User updateUser(User user) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'updateUser'");
    }

    @Override
    public Boolean existsByEmail(String email) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'existsByEmail'");
    }

    @Override
    public Boolean deleteUserById(long id) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'deleteUserById'");
    }
    
}
