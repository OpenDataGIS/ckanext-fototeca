    #    #esta parte debe recopilar el dataframe de pandas 
    #    def import_stage(self, harvest_object):
    #        # Aquí iría el código para crear o actualizar el conjunto de datos en CKAN.
    #        log.debug("In FototecaPGHarvester import stage")
    #
    #        context = {
    #            'model': model,
    #            'session': model.Session,
    #            'user': self._get_user_name(),
    #        }
    #        
    #        if not harvest_object:
    #            log.error('No harvest object received')
    #            return False   
    #        
    #        self._set_config(harvest_object.source.config)
    #        
    #        if self.force_import:
    #            status = 'change'
    #        else:
    #            status = self._get_object_extra(harvest_object, 'status')
    #        
    #        if status == 'delete':
    #            override_local_datasets = self.config.get("override_local_datasets", False)
    #            if override_local_datasets is True:
    #                # Delete package
    #                context.update({
    #                    'ignore_auth': True,
    #                })
    #                p.toolkit.get_action('package_delete')(context, {'id': harvest_object.package_id})
    #                log.info('The override_local_datasets configuration is %s. Package %s deleted with GUID: %s' % (override_local_datasets, harvest_object.package_id, harvest_object.guid))
    #
    #                return True
    #            
    #            else:
    #                log.info('The override_local_datasets configuration is %s. Package %s not deleted with GUID: %s' % (override_local_datasets, harvest_object.package_id, harvest_object.guid))
    #
    #                return 'unchanged'
    #
    #        # Check if harvest object has a non-empty content
    #        if harvest_object.content is None:
    #            self._save_object_error('Empty content for object {0}'.format(harvest_object.id),
    #                                    harvest_object, 'Import')
    #            return False
    #
    #        try:
    #            dataset = json.loads(harvest_object.content)
    #        except ValueError:
    #            self._save_object_error('Could not ateutil.parser.parse content for object {0}'.format(harvest_object.id),
    #                                    harvest_object, 'Import')
    #            return False
    #
    #        # Check if the dataset is a harvest source and we are not allowed to harvest it
    #        if dataset.get('type') == 'harvest' and self.config.get('allow_harvest_datasets', False) is False:
    #            log.warn('Remote dataset is a harvest source and allow_harvest_datasets is False, ignoring...')
    #            return True
    #
    #        return True