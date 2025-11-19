package com.api.nequiclone.service.interfaces;

import com.api.nequiclone.entity.User;

public interface UserService {

    User createUser(User user);

    User getUserById(Long id);

    User getUserByEmail(String email);

    User updateUser(User user);

    Boolean existsByEmail(String email);

    Boolean deleteUserById(long id);
}
