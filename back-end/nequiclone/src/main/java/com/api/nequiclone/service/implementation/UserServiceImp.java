package com.api.nequiclone.service.implementation;

import org.springframework.stereotype.Service;

import com.api.nequiclone.entity.User;
import com.api.nequiclone.service.interfaces.UserService;

@Service
public class UserServiceImp implements UserService {

    @Override
    public User createUser(User user) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'createUser'");
    }

    @Override
    public User getUserById(Long id) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'getUserById'");
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
